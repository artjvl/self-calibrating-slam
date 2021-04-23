import pathlib
import typing as tp
from abc import abstractmethod
from datetime import datetime

import numpy as np

from src.framework.graph.Graph import SubGraph
from src.framework.graph.GraphParser import GraphParser
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.nodes.topological import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.simulation.ParameterSet import ParameterSet
from src.framework.simulation.Simulation2D import Simulation2D
from src.framework.simulation.sensors.Sensor import SubSensor
from src.utils import GeoHash2D


class BiSimulation2D(object):

    def __init__(
            self,
            seed: int = 0
    ):
        self._rng = np.random.RandomState(seed)
        self._geo = GeoHash2D[int]()

        self._true = Simulation2D()
        self._perturbed = Simulation2D()
        translation: Vector2 = self._true.get_current_pose().translation()
        self._geo.add(translation[0], translation[1], self.get_current_id())

        self._parameters: tp.Optional[ParameterSet] = None

    # graph-construction
    def add_sensor(
            self,
            sensor_id: str,
            sensor_true: SubSensor,
            sensor_perturbed: SubSensor
    ) -> None:
        self._true.add_sensor(sensor_id, sensor_true)
        self._perturbed.add_sensor(sensor_id, sensor_perturbed)
        max_id: int = max(self._true.get_id(), self._perturbed.get_id())
        self._true.set_current_id(max_id)
        self._perturbed.set_current_id(max_id)

    def add_odometry(
            self,
            transformation: SE2,
            sensor_id: str
    ) -> None:
        true_sensor: SubSensor = self._true.get_sensor(sensor_id)
        true_measurement: SE2 = true_sensor.decompose(transformation)
        self._true.add_odometry(true_measurement, sensor_id)

        translation: Vector2 = self._true.get_current_pose().translation()
        self._geo.add(translation[0], translation[1], self._true.get_current_id())

        perturbed_measurement: SE2 = true_sensor.measure(true_measurement)
        self._perturbed.add_odometry(perturbed_measurement, sensor_id)

    def add_gps(
            self,
            translation: Vector2,
            sensor_id: str
    ) -> None:
        current_id: int = self.get_current_id()
        self.add_edge([current_id], translation, sensor_id)

    def add_edge(
            self,
            ids: tp.List[int],
            value: Supported,
            sensor_id: str
    ) -> None:
        true_sensor: SubSensor = self._true.get_sensor(sensor_id)
        true_measurement: Supported = true_sensor.decompose(value)
        self._true.add_edge(ids, true_measurement, sensor_id)

        perturbed_measurement: Supported = true_sensor.measure(true_measurement)
        self._perturbed.add_edge(ids, perturbed_measurement, sensor_id)

    def add_closure(
            self,
            distance: float,
            sensor_id: str,
            separation: int = 10,
            threshold: float = 1.
    ) -> None:
        if self._rng.uniform(0, 1) >= 1 - threshold:
            pose_ids: tp.List[int] = self._true.get_pose_ids()
            if len(pose_ids) > separation:
                current: NodeSE2 = self._true.get_current()
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

                    closure: NodeSE2 = self.get_true().get_node(closure_id)
                    transformation: SE2 = current.get_value() - closure.get_value()
                    self.add_edge([closure_id, current_id], transformation, sensor_id)

    def add_proximity(
            self,
            steps: int,
            sensor_id: str,
            threshold: float = 0.
    ) -> None:
        if self._rng.uniform(0, 1) >= 1 - threshold:
            pose_ids: tp.List[int] = self._true.get_pose_ids()
            if len(pose_ids) > steps:
                current: NodeSE2 = self._true.get_current()
                proximity_id: int = pose_ids[-1 - steps]
                proximity: NodeSE2 = self._true.get_node(proximity_id)

                transformation: SE2 = current.get_value() - proximity.get_value()
                ids: tp.List[int] = [proximity.get_id(), current.get_id()]
                self.add_edge(ids, transformation, sensor_id)

    def add_poses_edge(
            self,
            from_id: int,
            to_id: int,
            sensor_id: str
    ) -> None:
        transformation: SE2 = self._true.get_node(to_id).get_value() - self._true.get_node(from_id).get_value()
        self.add_edge([from_id, to_id], transformation, sensor_id)

    # logistics
    def fix(self):
        self._true.get_current().fix()
        self._perturbed.get_current().fix()

    def reset(self):
        self._true = Simulation2D()
        self._perturbed = Simulation2D()

    def save(
            self,
            name: tp.Optional[str] = None,
            folder: tp.Optional[pathlib.Path] = None
    ) -> None:
        if folder is None:
            folder: str = 'graphs/simulation'
        if name is None:
            name = datetime.now().strftime('%Y%m%d-%H%M%S')

        GraphParser.save_path_folder(self.get_true(), folder, name=f'{name}_true')
        GraphParser.save_path_folder(self.get_perturbed(), folder, name=f'{name}_perturbed')

    # graphs
    def get_graphs(self) -> tp.Tuple[SubGraph, SubGraph]:
        return self.get_true(), self.get_perturbed()

    def get_true(self) -> SubGraph:
        return self._true.get_graph()

    def get_perturbed(self) -> SubGraph:
        return self._perturbed.get_graph()

    def get_current_id(self) -> int:
        assert self._true.get_current_id() == self._perturbed.get_current_id()
        return self._true.get_current_id()

    # parameters
    def set_parameters(self, parameters: ParameterSet) -> None:
        self._parameters = parameters

    def has_parameters(self) -> bool:
        return self._parameters is not None

    def get_parameters(self) -> ParameterSet:
        assert self.has_parameters()
        return self._parameters

    # simulation
    def simulate(self) -> tp.Tuple[SubGraph, SubGraph]:
        self._simulate()
        true, perturbed = self.get_graphs()
        self.save()
        self.reset()
        return true, perturbed

    @abstractmethod
    def _simulate(self):
        pass
