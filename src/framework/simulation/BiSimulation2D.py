import pathlib
import typing as tp
from abc import abstractmethod
from datetime import datetime

import numpy as np
from src.framework.graph.Graph import SubGraph, SubEdge
from src.framework.graph.GraphManager import SubGraphManager
from src.framework.graph.GraphParser import GraphParser
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.nodes.SpatialNode import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.simulation.ParameterSet import ParameterSet
from src.framework.simulation.Simulation2D import Simulation2D
from src.framework.simulation.sensors.Sensor import SubSensor
from src.utils import GeoHash2D


class BiSimulation2D(object):

    # rng
    _seed: tp.Optional[int]
    _rng = np.random.RandomState

    # data
    _geo: GeoHash2D[int]
    _truth: Simulation2D
    _perturbed: Simulation2D

    # parameters
    _parameters: tp.Optional[ParameterSet]

    def __init__(
            self,
            seed: tp.Optional[int] = None
    ):
        # rng
        self._seed = seed
        self.set_seed(self._seed)
        self.init()

        # parameters
        self._parameters = None

    def init(self) -> None:
        self._truth = Simulation2D()
        self._perturbed = Simulation2D()
        # self._perturbed.get_graph().assign_truth(self._truth.get_graph())

        self._geo = GeoHash2D[int]()
        translation: Vector2 = self._truth.get_current().get_value().translation()
        self._geo.add(translation[0], translation[1], self.get_current_id())

    # sensors
    def add_sensor(
            self,
            sensor_id: str,
            sensor_truth: SubSensor,
            sensor_perturbed: SubSensor
    ) -> None:
        """ Adds a sensor with <sensor_id>. """

        sensor_truth.set_seed(self._seed)
        self._truth.add_sensor(sensor_id, sensor_truth)
        sensor_perturbed.set_seed(self._seed)
        self._perturbed.add_sensor(sensor_id, sensor_perturbed)

    def align_ids(self) -> None:
        """ Aligns the current-pose-id of each simulation. """

        truth_manager: SubGraphManager = self._truth.get_graph_manager()
        perturbed_manager: SubGraphManager = self._perturbed.get_graph_manager()

        id_ = max(truth_manager.get_count(), perturbed_manager.get_count())
        truth_manager.set_counter(id_)
        perturbed_manager.set_counter(id_)

    def get_sensors(self, sensor_id: str) -> tp.Tuple[SubSensor, SubSensor]:
        return self._truth.get_sensor(sensor_id), self._perturbed.get_sensor(sensor_id)

    # edges
    def add_edge(
            self,
            ids: tp.List[int],
            value: Supported,
            sensor_id: str
    ) -> None:
        """ Adds a new edge between <ids> with <value>, as measured by <sensor_id>. """

        # add new 'truth' edge
        truth_sensor: SubSensor = self._truth.get_sensor(sensor_id)
        truth_measurement: Supported = truth_sensor.decompose(value)
        truth_edge: SubEdge = self._truth.add_edge_from_value(sensor_id, ids, truth_measurement)

        # add new 'perturbed' edge
        perturbed_measurement: Supported = truth_sensor.measure(truth_measurement)
        perturbed_edge: SubEdge = self._perturbed.add_edge_from_value(sensor_id, ids, perturbed_measurement)
        perturbed_edge.assign_truth(truth_edge)

        # align ids because of potential edge parameters
        self.align_ids()

    def add_poses_edge(
            self,
            sensor_id: str,
            from_id: int,
            to_id: int
    ) -> None:
        """ Adds an edge between <from_id> and <to_id> with the 'truth' transformation, as measured by <sensor_id>. """

        transformation: SE2 = self._truth.get_node(to_id).get_value() - self._truth.get_node(from_id).get_value()
        self.add_edge([from_id, to_id], transformation, sensor_id)

    # odometry
    def add_odometry(
            self,
            sensor_id: str,
            transformation: SE2
    ) -> None:
        """ Adds a new pose-node and edge with <transformation>, as measured by <sensor_id>. """

        # add new 'truth' pose and edge
        truth_sensor: SubSensor = self._truth.get_sensor(sensor_id)
        truth_measurement: SE2 = truth_sensor.decompose(transformation)
        truth_edge: SubEdge = self._truth.add_odometry(sensor_id, truth_measurement)

        # store new 'truth' pose in geo-hashmap
        translation: Vector2 = self._truth.get_current().get_value().translation()
        self._geo.add(translation[0], translation[1], self._truth.get_current().get_id())

        # add new 'perturbed' pose and edge
        perturbed_measurement: SE2 = truth_sensor.measure(truth_measurement)
        perturbed_edge: SubEdge = self._perturbed.add_odometry(sensor_id, perturbed_measurement)
        perturbed_edge.assign_truth(truth_edge)

        # align ids because of potential edge parameters
        self.align_ids()

    # gps
    def add_gps(
            self,
            sensor_id: str,
            translation: tp.Optional[Vector2] = None
    ) -> None:
        """ Adds a GPS measurement (i.e., location prior) at <translation>, as measured by <sensor_id>. """

        if translation is None:
            translation = self._truth.get_current().get_value().translation()
        current_id: int = self.get_current_id()
        self.add_edge([current_id], translation, sensor_id)

    # loop-closure
    def roll_closure(
            self,
            sensor_id: str,
            distance: float,
            separation: int = 10,
            threshold: float = 0.
    ) -> None:
        """ Creates a loop-closure constraint with probability <threshold>. """

        if self._rng.uniform(0, 1) >= threshold:
            self.try_closure(sensor_id, distance, separation)

    def try_closure(
            self,
            sensor_id: str,
            distance: float,
            separation: int = 10
    ) -> None:
        """
        Creates a loop-closure constraint IF POSSIBLE with the oldest node within <distance> and separated by
        <separation> ids, with the 'truth' transformation, as measurement by <sensor_id>.
        """

        pose_ids: tp.List[int] = self._truth.get_pose_ids()
        if len(pose_ids) > separation:
            current: NodeSE2 = self._truth.get_current()
            location: Vector2 = current.get_value().translation()

            closures: tp.List[int] = self._geo.find_within(location[0], location[1], distance)
            filtered: tp.List[int] = pose_ids[:-1 - separation]
            matches: tp.List[int] = []
            for closure in closures:
                if closure in filtered:
                    matches.append(closure)
            if matches:
                closure_id: int = matches[0]
                # closure_id: int = self._rng.choice(closures)
                current_id: int = self.get_current_id()
                self.add_poses_edge(sensor_id, closure_id, current_id)

    # proximity constraint
    def roll_proximity(
            self,
            sensor_id: str,
            steps: int,
            threshold: float = 0.
    ) -> None:
        """ Creates a proximity constraint with probability <threshold>. """

        if self._rng.uniform(0, 1) >= threshold:
            self.try_proximity(sensor_id, steps)

    def try_proximity(
            self,
            sensor_id: str,
            steps: int
    ) -> None:
        """
        Creates a proximity constraint IF POSSIBLE with the node separated by <steps>, with the 'truth' transformation,
        as measurement by <sensor_id>.
        """

        pose_ids: tp.List[int] = self._truth.get_pose_ids()
        if len(pose_ids) > steps:
            current_id: int = self._truth.get_current().get_id()
            proximity_id: int = pose_ids[-1 - steps]
            self.add_poses_edge(sensor_id, proximity_id, current_id)

    # logistics
    def snapshot(self):
        truth_graph: SubGraph = self._truth.snapshot()
        perturbed_graph: SubGraph = self._perturbed.snapshot()
        truth_graph.assign_truth(perturbed_graph, is_deep=False)

    def set_timestamp(self, timestamp: float):
        """ Sets the timestamp of both simulations. """

        self._truth.set_timestamp(timestamp)
        self._perturbed.set_timestamp(timestamp)

    def increment_timestamp(self, delta: float):
        """ Increments the timestamp of both simulations by <delta>. """

        self._truth.increment_timestamp(delta)
        self._perturbed.increment_timestamp(delta)

    def fix(self):
        """ Fixes the current pose-node. """

        self._truth.get_current().fix()
        self._perturbed.get_current().fix()

    def save(
            self,
            name: tp.Optional[str] = None,
            folder: tp.Optional[pathlib.Path] = None
    ) -> None:
        if folder is None:
            folder: str = 'graphs/simulation'
        if name is None:
            name = datetime.now().strftime('%Y%m%d-%H%M%S')

        GraphParser.save_path_folder(self.get_truth(), folder, name=f'{name}_truth')
        GraphParser.save_path_folder(self.get_perturbed(), folder, name=f'{name}_perturbed')

    # graphs
    def get_graphs(self) -> tp.Tuple[SubGraph, SubGraph]:
        """ Returns the 'truth' and 'perturbed' graphs. """
        return self.get_truth(), self.get_perturbed()

    def get_truth(self) -> SubGraph:
        """ Returns the 'truth' graph. """
        return self._truth.get_graph()

    def get_perturbed(self) -> SubGraph:
        """ Returns the 'perturbed' graph. """
        return self._perturbed.get_graph()

    def get_current_id(self) -> int:
        """ Returns the synchronised id of the current pose-node. """
        return self._truth.get_current().get_id()

    def get_current(self) -> NodeSE2:
        return self._truth.get_current()

    def get_current_pose(self) -> SE2:
        return self._truth.get_current().get_value()

    # parameters
    def set_parameters(self, parameters: ParameterSet) -> None:
        self._parameters = parameters

    def has_parameters(self) -> bool:
        return self._parameters is not None

    def get_parameters(self) -> ParameterSet:
        assert self.has_parameters()
        return self._parameters

    # seed
    def get_rng(self) -> np.random.RandomState:
        return self._rng

    def set_seed(self, seed: tp.Optional[int] = None):
        """
        Sets the seed for the RNG of this simulation. In order for the seed to propagate to the Sensors, set the
        seed before adding the Sensors!
        """
        self._seed = seed
        self._rng = np.random.RandomState(self._seed)

    # simulation
    def simulate(self) -> tp.Tuple[SubGraph, SubGraph]:
        self._simulate()
        truth, perturbed = self.get_graphs()
        self.save()
        self.init()
        return truth, perturbed

    @abstractmethod
    def _simulate(self) -> None:
        """ Override this method to define a simulation that modifies '_truth' and '_perturbed'. """
        pass
