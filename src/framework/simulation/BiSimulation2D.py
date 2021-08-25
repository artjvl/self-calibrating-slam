import pathlib
import sys
import typing as tp
from abc import abstractmethod
from datetime import datetime

import numpy as np
from src.framework.graph.GraphParser import GraphParser
from src.framework.math.lie.transformation import SE2
from src.framework.optimiser.Optimiser import Optimiser
from src.framework.simulation.ConfigurationSet import ConfigurationSet
from src.framework.simulation.Parameter import StaticParameter, SlidingParameter, OldSlidingParameter
from src.framework.simulation.Sensor import SensorFactory
from src.framework.simulation.SubSimulation2D import SubSubSimulation2D, SubSimulation2D, PlainSubSimulation2D
from src.utils import GeoHash2D

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.square import SubSquare
    from src.framework.math.matrix.vector import Vector2
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.Graph import SubGraph, SubEdge
    from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
    from src.framework.graph.types.nodes.SpatialNode import NodeSE2
    from src.framework.simulation.Parameter import SubParameter
    from src.framework.simulation.Sensor import SubSensor
    from src.framework.simulation.SubSimulation2D import SubSubSimulation2D

SubBiSimulation2D = tp.TypeVar('SubBiSimulation2D', bound='BiSimulation2D')


class BiSimulation2D(object):
    _optimiser: tp.Optional[Optimiser]
    _sim_type: tp.Type['SubSubSimulation2D']

    # rng
    _sensor_seed: tp.Optional[int]
    _path_rng: np.random.RandomState
    _constraint_rng: np.random.RandomState

    # data
    _geo: GeoHash2D[int]
    _truth: 'SubSubSimulation2D'
    _estimate: 'SubSubSimulation2D'

    # parameters
    _config: tp.Optional[ConfigurationSet]

    def __init__(
            self,
            sim_type: tp.Type['SubSubSimulation2D'] = None,
            optimiser: tp.Optional[Optimiser] = None,
            path_seed: tp.Optional[int] = None,
            constraint_seed: tp.Optional[int] = None,
            sensor_seed: tp.Optional[int] = None
    ):
        self._sim_type = sim_type
        self._optimiser = optimiser

        # rng
        self.set_path_rng(path_seed)
        self.set_constraint_rng(constraint_seed)
        self._sensor_seed = sensor_seed

        # parameters
        self._config = None

    def reset(self) -> None:
        self._truth = PlainSubSimulation2D()
        self._estimate = self._sim_type(optimiser=self._optimiser)
        self._estimate.get_graph().assign_truth(self._truth.get_graph())

        self._geo = GeoHash2D[int]()
        translation: 'Vector2' = self._truth.get_current().get_value().translation()
        self._geo.add(translation[0], translation[1], self.get_current_id())

    def set_sim_type(self, sim_type: tp.Type['SubSubSimulation2D']):
        self._sim_type = sim_type
        self.reset()

    def has_sim_type(self) -> bool:
        return self._sim_type is not None

    # sensors
    def add_sensor(
            self,
            sensor_name: str,
            type_: tp.Type['Quantity'],
            info_matrix_truth: 'SubSquare',
            info_matrix_estimate: 'SubSquare'
    ) -> None:
        self.add_sensor_with_info_matrix(sensor_name, type_, info_matrix_truth, info_matrix_estimate)

    def add_sensor_with_info_matrix(
            self,
            sensor_name: str,
            type_: tp.Type['Quantity'],
            info_matrix_truth: 'SubSquare',
            info_matrix_estimate: 'SubSquare'
    ) -> None:
        self._truth.add_sensor(
            sensor_name, SensorFactory.from_value(
                type_,
                info_matrix=info_matrix_truth,
                seed=self._sensor_seed
            )
        )
        self._estimate.add_sensor(
            sensor_name, SensorFactory.from_value(
                type_,
                info_matrix=info_matrix_estimate,
                seed=self._sensor_seed
            )
        )

    def add_sensor_with_cov_matrix(
            self,
            sensor_name: str,
            type_: tp.Type['Quantity'],
            cov_matrix_truth: 'SubSquare',
            cov_matrix_estimate: 'SubSquare'
    ) -> None:
        self.add_sensor_with_info_matrix(sensor_name, type_, cov_matrix_truth.inverse(), cov_matrix_estimate.inverse())

    def has_sensor(self, sensor_name: str) -> bool:
        return self._truth.has_sensor(sensor_name)

    def get_truth_sensor(self, sensor_name: str) -> 'SubSensor':
        return self._truth.get_sensor(sensor_name)

    def get_estimate_sensor(self, sensor_name: str) -> 'SubSensor':
        return self._estimate.get_sensor(sensor_name)

    def set_truth_info_matrix(self, sensor_name: str, info_matrix: 'SubSquare') -> None:
        self.get_truth_sensor(sensor_name).set_info_matrix(info_matrix)

    def set_truth_cov_matrix(self, sensor_name: str, cov_matrix: 'SubSquare') -> None:
        self.get_truth_sensor(sensor_name).set_cov_matrix(cov_matrix)

    def get_sensors(self, sensor_name: str) -> tp.Tuple['SubSensor', 'SubSensor']:
        return self.get_truth_sensor(sensor_name), self.get_estimate_sensor(sensor_name)

    # parameters
    def add_truth_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            index: int = 0,
            is_visible: bool = True
    ) -> None:
        parameter: 'SubParameter' = StaticParameter(
            value=value,
            specification=specification,
            index=index,
            is_visible=is_visible
        )
        self._truth.add_parameter(sensor_name, parameter_name, parameter)

    def update_truth_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity'
    ) -> None:
        self._truth.update_parameter(sensor_name, parameter_name, value)

    def add_sliding_estimate_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            window: int,
            index: int = 0
    ) -> None:
        parameter: 'SubParameter' = SlidingParameter(
            value=value,
            specification=specification,
            window_size=window,
            index=index
        )
        self._estimate.add_parameter(sensor_name, parameter_name, parameter)

    def add_old_sliding_estimate_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            window: int,
            index: int = 0
    ) -> None:
        parameter: 'SubParameter' = OldSlidingParameter(
            value=value,
            specification=specification,
            window_size=window,
            index=index
        )
        self._estimate.add_parameter(sensor_name, parameter_name, parameter)

    def add_constant_estimate_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            index: int = 0
    ) -> None:
        parameter: 'SubParameter' = StaticParameter(
            value=value,
            specification=specification,
            index=index,
            is_visible=True
        )
        self._estimate.add_parameter(sensor_name, parameter_name, parameter)

    def update_constant_estimate_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity'
    ) -> None:
        assert self.has_sensor(sensor_name)
        sensor: 'SubSensor' = self._estimate.get_sensor(sensor_name)
        assert sensor.update_parameter(parameter_name, value)

    # edges
    def add_edge(
            self,
            sensor_name: str,
            ids: tp.List[int],
            value: 'Quantity'
    ) -> None:
        """ Adds a new edge between <ids> with <value>, as measured by <sensor_name>. """

        self.align_ids()
        truth_sensor, estimate_sensor = self.get_sensors(sensor_name)

        # add new 'truth' edge
        truth_measurement: 'Quantity' = truth_sensor.decompose(value)
        truth_edge: 'SubEdge' = self._truth.add_edge_from_value(sensor_name, ids, truth_measurement)

        # add new 'perturbed' edge
        estimate_measurement: 'Quantity' = truth_sensor.measure(truth_measurement)
        estimate_edge: 'SubEdge' = self._estimate.add_edge_from_value(sensor_name, ids, estimate_measurement)
        self._estimate.report_closure()
        estimate_edge.assign_truth(truth_edge)

    def add_poses_edge(
            self,
            sensor_name: str,
            from_id: int,
            to_id: int
    ) -> None:
        """ Adds an edge between <from_id> and <to_id> with the 'truth' transformation, as measured by <sensor_name>. """

        transformation: SE2 = self._truth.get_node(to_id).get_value() - self._truth.get_node(from_id).get_value()
        self.add_edge(sensor_name, [from_id, to_id], transformation)

    # odometry
    def add_odometry(
            self,
            sensor_name: str,
            transformation: SE2
    ) -> None:
        """ Adds a new pose-node and edge with <transformation>, as measured by <sensor_name>. """
        self.align_ids()

        # add new 'truth' pose and edge
        truth_sensor: 'SubSensor' = self._truth.get_sensor(sensor_name)
        truth_measurement: SE2 = truth_sensor.decompose(transformation)
        truth_node, truth_edge = self._truth.add_odometry(sensor_name, truth_measurement)

        # store new 'truth' pose in geo-hashmap
        translation: 'Vector2' = self._truth.get_current().get_value().translation()
        self._geo.add(translation[0], translation[1], self._truth.get_current().get_id())

        # add new 'perturbed' pose and edge
        estimate_measurement: SE2 = truth_sensor.measure(truth_measurement)
        estimate_node, estimate_edge = self._estimate.add_odometry(sensor_name, estimate_measurement)
        estimate_node.assign_truth(truth_node)
        estimate_edge.assign_truth(truth_edge)

    def add_odometry_to(
            self,
            sensor_name: str,
            pose: SE2
    ) -> None:
        """ Adds a new pose-node and edge at <pose>, as measured by <sensor_name>. """
        transformation: SE2 = pose - self.get_current_pose()
        self.add_odometry(sensor_name, transformation)

    # gps
    def add_gps(
            self,
            sensor_name: str,
            translation: tp.Optional['Vector2'] = None
    ) -> None:
        """ Adds a GPS measurement (i.e., location prior) at <translation>, as measured by <sensor_name>. """

        if translation is None:
            translation = self._truth.get_current().get_value().translation()
        current_id: int = self.get_current_id()
        self.add_edge(sensor_name, [current_id], translation)

    # loop-closure
    def roll_closure(
            self,
            sensor_name: str,
            distance: float,
            separation: int = 10,
            threshold: float = 0.
    ) -> None:
        """ Creates a loop-closure constraint with probability <threshold>. """

        if self._constraint_rng.uniform(0, 1) >= threshold:
            self.try_closure(sensor_name, distance, separation)

    def try_closure(
            self,
            sensor_name: str,
            distance: float,
            separation: int = 10
    ) -> None:
        """
        Creates a loop-closure constraint IF POSSIBLE with the oldest node within <distance> and separated by
        <separation> ids, with the 'truth' transformation, as measurement by <sensor_name>.
        """

        pose_ids: tp.List[int] = self._truth.get_pose_ids()
        if len(pose_ids) > separation:
            current: 'NodeSE2' = self._truth.get_current()
            location: 'Vector2' = current.get_value().translation()

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
                self.add_poses_edge(sensor_name, closure_id, current_id)

    # proximity constraint
    def roll_proximity(
            self,
            sensor_name: str,
            steps: int,
            threshold: float = 0.
    ) -> None:
        """ Creates a proximity constraint with probability <threshold>. """

        if self._constraint_rng.uniform(0, 1) >= threshold:
            self.try_proximity(sensor_name, steps)

    def try_proximity(
            self,
            sensor_name: str,
            steps: int
    ) -> None:
        """
        Creates a proximity constraint IF POSSIBLE with the node separated by <steps>, with the 'truth' transformation,
        as measurement by <sensor_name>.
        """

        pose_ids: tp.List[int] = self._truth.get_pose_ids()
        if len(pose_ids) > steps:
            current_id: int = self._truth.get_current().get_id()
            proximity_id: int = pose_ids[-1 - steps]
            self.add_poses_edge(sensor_name, proximity_id, current_id)

    # logistics
    def align_ids(self) -> None:
        """ Aligns the current-pose-id of each simulation. """

        id_ = max(self._truth.get_id(), self._estimate.get_id())
        self._truth.set_count(id_)
        self._estimate.set_count(id_)

    def get_timestamp(self) -> float:
        return self._truth.get_timestamp()

    def fix(self):
        """ Fixes the current pose-node. """

        self._truth.get_current().fix()
        self._estimate.get_current().fix()

    def save(
            self,
            name: tp.Optional[str] = None,
            folder: tp.Optional[pathlib.Path] = None
    ) -> None:
        if folder is None:
            folder: str = 'graphs/simulation'
        if name is None:
            name = datetime.now().strftime('%Y%m%d-%H%M%S')

        GraphParser.save_path_folder(self.get_truth_graph(), folder, name=f'{name}_truth')
        GraphParser.save_path_folder(self.get_estimate_graph(), folder, name=f'{name}_perturbed')

    # graphs
    def get_graphs(self) -> tp.Tuple['SubGraph', 'SubGraph']:
        """ Returns the 'truth' and 'perturbed' graphs. """
        return self.get_truth_graph(), self.get_estimate_graph()

    def get_truth_graph(self) -> 'SubGraph':
        """ Returns the 'truth' graph. """
        return self._truth.get_graph()

    def get_estimate_graph(self) -> 'SubGraph':
        """ Returns the 'perturbed' graph. """
        return self._estimate.get_graph()

    # current
    def get_current_node(self) -> 'NodeSE2':
        return self._truth.get_current()

    def get_current_pose(self) -> SE2:
        return self.get_current_node().get_value()

    def get_current_id(self) -> int:
        """ Returns the synchronised id of the current pose-node. """
        return self.get_current_node().get_id()

    # parameters
    def set_config(self, config: ConfigurationSet) -> None:
        self._config = config

    def has_config(self) -> bool:
        return self._config is not None

    def get_config(self) -> ConfigurationSet:
        assert self.has_config()
        return self._config

    # seed
    def get_path_rng(self) -> np.random.RandomState:
        return self._path_rng

    def set_path_rng(self, seed: tp.Optional[int] = None) -> None:
        self._path_rng = np.random.RandomState(seed)

    def set_constraint_rng(self, seed: tp.Optional[int] = None) -> None:
        self._constraint_rng = np.random.RandomState(seed)

    def set_sensor_seed(self, seed: tp.Optional[int] = None) -> None:
        self._sensor_seed = seed

    # simulation
    def step(self, delta: float):
        truth_graph: 'SubGraph' = self._truth.step(delta)
        estimate_graph: 'SubGraph' = self._estimate.step(delta)
        sys.__stdout__.write(f'\rstep: {self.get_timestamp():.2f}')
        sys.__stdout__.flush()

    def simulate(self) -> tp.Tuple['SubGraph', 'SubGraph']:
        self.init()
        assert self.has_sim_type()

        self.loop()

        sys.__stdout__.write(f"\rSimulation '{self.__class__.__name__}' done!\n")
        sys.__stdout__.flush()
        truth, perturbed = self.get_graphs()
        self.save()
        self.reset()
        return truth, perturbed

    @abstractmethod
    def init(self) -> None:
        """ Override this method to define the initialisation of simulation. """
        pass

    @abstractmethod
    def loop(self) -> None:
        """ Override this method to define the simulation loop header. """
        pass
