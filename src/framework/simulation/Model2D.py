import pathlib
import sys
import typing as tp
from abc import abstractmethod, ABC
from datetime import datetime

import numpy as np
from src.framework.graph.GraphParser import GraphParser
from src.framework.math.lie.transformation import SE2
from src.framework.optimiser.Optimiser import Optimiser
from src.framework.simulation.ConfigurationSet import ConfigurationSet
from src.framework.simulation.Parameter import StaticParameter, SlidingParameter, OldSlidingParameter
from src.framework.simulation.PostAnalyser import VarianceAnalyser
from src.framework.simulation.Sensor import SensorFactory
from src.framework.simulation.SubModel2D import SubSubSimulation2D, PlainSubModel2D, PostSubModel2D, \
    SlidingSubModel2D, IncrementalSubModel2D
from src.utils import GeoHash2D

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.square import SubSquare
    from src.framework.math.matrix.vector import Vector2
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.Graph import SubGraph, SubEdge
    from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
    from src.framework.graph.types.nodes.SpatialNode import NodeSE2
    from src.framework.simulation.Parameter import SubParameter
    from src.framework.simulation.PostAnalyser import SubPostAnalyser
    from src.framework.simulation.Sensor import SubSensor
    from src.framework.simulation.SubModel2D import SubSubSimulation2D

SubModel2D = tp.TypeVar('SubModel2D', bound='Model2D')


class BaseModel2D(object):

    # simulation
    _geo: GeoHash2D[int]
    _truth_sim: 'SubSubSimulation2D'
    _estimate_sim: tp.Optional['SubSubSimulation2D']

    # rng
    _path_rng: np.random.RandomState
    _constraint_rng: np.random.RandomState
    _sensor_seed: tp.Optional[int]

    # parameters
    _config: tp.Optional[ConfigurationSet]

    def __init__(
            self,
            path_seed: tp.Optional[int] = None,
            constraint_seed: tp.Optional[int] = None,
            sensor_seed: tp.Optional[int] = None
    ):
        # simulation
        self._geo = GeoHash2D[int]()

        # rng
        self.set_path_rng(path_seed)
        self.set_constraint_rng(constraint_seed)
        self._sensor_seed = sensor_seed

        self.reset()

    @abstractmethod
    def truth_sim(self) -> 'SubSubSimulation2D':
        pass

    @abstractmethod
    def estimate_sim(self) -> 'SubSubSimulation2D':
        pass

    def reset(self) -> None:
        truth_sim: 'SubSubSimulation2D' = self.truth_sim()
        estimate_sim: 'SubSubSimulation2D' = self.estimate_sim()

        # reset graphs
        truth_sim.reset()
        estimate_sim.reset()
        estimate_sim.graph().assign_truth(truth_sim.graph())

        # geo
        self._geo.reset()
        translation: 'Vector2' = truth_sim.get_current().get_value().translation()
        self._geo.add(translation[0], translation[1], self.get_current_id())

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
        self.truth_sim().add_sensor(
            sensor_name, SensorFactory.from_value(
                type_,
                info_matrix=info_matrix_truth,
                seed=self._sensor_seed
            )
        )
        self.estimate_sim().add_sensor(
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
        return self.truth_sim().has_sensor(sensor_name)

    def get_truth_sensor(self, sensor_name: str) -> 'SubSensor':
        return self.truth_sim().get_sensor(sensor_name)

    def get_estimate_sensor(self, sensor_name: str) -> 'SubSensor':
        return self.estimate_sim().get_sensor(sensor_name)

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
        self.truth_sim().add_parameter(sensor_name, parameter_name, parameter)

    def update_truth_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity'
    ) -> None:
        self.truth_sim().update_parameter(sensor_name, parameter_name, value)

    # edges
    def add_edge(
            self,
            sensor_name: str,
            ids: tp.List[int],
            value: 'Quantity'
    ) -> None:
        """ Adds a new edge between <ids> with <value>, as measured by <sensor_name>. """

        truth_sim: 'SubSubSimulation2D' = self.truth_sim()
        estimate_sim: 'SubSubSimulation2D' = self.estimate_sim()
        self.align_ids()

        # add new 'truth' edge
        truth_sensor: 'SubSensor' = truth_sim.get_sensor(sensor_name)
        truth_measurement: 'Quantity' = truth_sensor.decompose(value)
        truth_edge: 'SubEdge' = truth_sim.add_edge_from_value(sensor_name, ids, truth_measurement)

        # add new 'perturbed' edge
        estimate_measurement: 'Quantity' = truth_sensor.measure(truth_measurement)
        estimate_edge: 'SubEdge' = estimate_sim.add_edge_from_value(sensor_name, ids, estimate_measurement)
        estimate_sim.report_closure()
        estimate_edge.assign_truth(truth_edge)

    def add_poses_edge(
            self,
            sensor_name: str,
            from_id: int,
            to_id: int
    ) -> None:
        """ Adds an edge between <from_id> and <to_id> with the 'truth' transformation, as measured by <sensor_name>. """

        truth_sim: 'SubSubSimulation2D' = self.truth_sim()
        transformation: SE2 = truth_sim.get_node(to_id).get_value() - truth_sim.get_node(from_id).get_value()
        self.add_edge(sensor_name, [from_id, to_id], transformation)

    # odometry
    def add_odometry(
            self,
            sensor_name: str,
            transformation: SE2
    ) -> None:
        """ Adds a new pose-node and edge with <transformation>, as measured by <sensor_name>. """

        self.align_ids()
        truth_sim: 'SubSubSimulation2D' = self.truth_sim()
        estimate_sim: 'SubSubSimulation2D' = self.estimate_sim()

        # add new 'truth' pose and edge
        truth_sensor: 'SubSensor' = truth_sim.get_sensor(sensor_name)
        truth_measurement: SE2 = truth_sensor.decompose(transformation)
        truth_node, truth_edge = truth_sim.add_odometry(sensor_name, truth_measurement)

        # store new 'truth' pose in geo-hashmap
        translation: 'Vector2' = truth_sim.get_current().get_value().translation()
        self._geo.add(translation[0], translation[1], truth_sim.get_current().get_id())

        # add new 'perturbed' pose and edge
        estimate_measurement: SE2 = truth_sensor.measure(truth_measurement)
        estimate_node, estimate_edge = estimate_sim.add_odometry(sensor_name, estimate_measurement)
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
            translation = self.get_current_pose().translation()
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

        truth_sim: 'SubSubSimulation2D' = self.truth_sim()

        pose_ids: tp.List[int] = truth_sim.get_pose_ids()
        if len(pose_ids) > separation:
            current: 'NodeSE2' = truth_sim.get_current()
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

        truth_sim: 'SubSubSimulation2D' = self.truth_sim()

        pose_ids: tp.List[int] = truth_sim.get_pose_ids()
        if len(pose_ids) > steps:
            current_id: int = truth_sim.get_current().get_id()
            proximity_id: int = pose_ids[-1 - steps]
            self.add_poses_edge(sensor_name, proximity_id, current_id)

    # logistics
    def align_ids(self) -> None:
        """ Aligns the current-pose-id of each simulation. """

        truth_sim: 'SubSubSimulation2D' = self.truth_sim()
        estimate_sim: 'SubSubSimulation2D' = self.estimate_sim()
        id_ = max(truth_sim.get_id(), estimate_sim.get_id())
        truth_sim.set_count(id_)
        estimate_sim.set_count(id_)

    def get_timestamp(self) -> float:
        return self.truth_sim().get_timestamp()

    def step(self, delta: float) -> None:
        self.truth_sim().step(delta)
        self.estimate_sim().step(delta)
        self.print(f'step: {self.get_timestamp():.2f}')

    def fix(self) -> None:
        """ Fixes the current pose-node. """

        self.truth_sim().get_current().fix()
        self.estimate_sim().get_current().fix()

    # current
    def get_current_node(self) -> 'NodeSE2':
        return self.truth_sim().get_current()

    def get_current_pose(self) -> SE2:
        return self.get_current_node().get_value()

    def get_current_id(self) -> int:
        """ Returns the synchronised id of the current pose-node. """
        return self.get_current_node().get_id()

    # seed
    def get_path_rng(self) -> np.random.RandomState:
        return self._path_rng

    def set_path_rng(self, seed: tp.Optional[int] = None) -> None:
        self._path_rng = np.random.RandomState(seed)

    def set_constraint_rng(self, seed: tp.Optional[int] = None) -> None:
        self._constraint_rng = np.random.RandomState(seed)

    def set_sensor_seed(self, seed: tp.Optional[int] = None) -> None:
        self._sensor_seed = seed

    # tools
    @staticmethod
    def print(text: str) -> None:
        sys.__stdout__.write(f'\r{text}')
        sys.__stdout__.flush()

    def save(
            self,
            name: tp.Optional[str] = None,
            folder: tp.Optional[pathlib.Path] = None
    ) -> None:
        if folder is None:
            folder: str = 'graphs/simulation'
        if name is None:
            name = datetime.now().strftime('%Y%m%d-%H%M%S')

        GraphParser.save_path_folder(self.truth_graph(), folder, name=f'{name}_truth')
        GraphParser.save_path_folder(self.estimate_graph(), folder, name=f'{name}_perturbed')

    def truth_graph(self) -> 'SubGraph':
        return self.truth_sim().graph()

    def estimate_graph(self) -> 'SubGraph':
        return self.estimate_sim().graph()


class Model2D(BaseModel2D):

    def __init__(
            self,
            sim_type: tp.Type['SubSubSimulation2D'],
            optimiser: tp.Optional[Optimiser] = None,
            path_seed: tp.Optional[int] = None,
            constraint_seed: tp.Optional[int] = None,
            sensor_seed: tp.Optional[int] = None
    ):

        # simulation
        self._truth_sim = PlainSubModel2D()
        self._estimate_sim = sim_type(optimiser=optimiser)

        super().__init__(
            path_seed=path_seed,
            constraint_seed=constraint_seed,
            sensor_seed=sensor_seed
        )

        # parameters
        self._config = None

    def truth_sim(self) -> 'SubSubSimulation2D':
        return self._truth_sim

    def estimate_sim(self) -> 'SubSubSimulation2D':
        return self._estimate_sim

    # config
    def set_config(self, config: ConfigurationSet) -> None:
        self._config = config

    def has_config(self) -> bool:
        return self._config is not None

    def get_config(self) -> ConfigurationSet:
        assert self.has_config()
        return self._config


class PlainModel2D(Model2D, ABC):

    def __init__(
            self,
            optimiser: tp.Optional[Optimiser] = None,
            path_seed: tp.Optional[int] = None,
            constraint_seed: tp.Optional[int] = None,
            sensor_seed: tp.Optional[int] = None
    ):
        super().__init__(
            sim_type=PlainSubModel2D,
            optimiser=optimiser,
            path_seed=path_seed,
            constraint_seed=constraint_seed,
            sensor_seed=sensor_seed
        )


class IncrementalModel2D(Model2D, ABC):

    def __init__(
            self,
            optimiser: tp.Optional[Optimiser] = None,
            path_seed: tp.Optional[int] = None,
            constraint_seed: tp.Optional[int] = None,
            sensor_seed: tp.Optional[int] = None
    ):
        super().__init__(
            sim_type=IncrementalSubModel2D,
            optimiser=optimiser,
            path_seed=path_seed,
            constraint_seed=constraint_seed,
            sensor_seed=sensor_seed
        )

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
        self.estimate_sim().add_parameter(sensor_name, parameter_name, parameter)

    def update_constant_estimate_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity'
    ) -> None:
        assert self.has_sensor(sensor_name)
        sensor: 'SubSensor' = self.estimate_sim().get_sensor(sensor_name)
        assert sensor.update_parameter(parameter_name, value)


class SlidingModel2D(Model2D, ABC):

    def __init__(
            self,
            optimiser: tp.Optional[Optimiser] = None,
            path_seed: tp.Optional[int] = None,
            constraint_seed: tp.Optional[int] = None,
            sensor_seed: tp.Optional[int] = None
    ):
        super().__init__(
            sim_type=SlidingSubModel2D,
            optimiser=optimiser,
            path_seed=path_seed,
            constraint_seed=constraint_seed,
            sensor_seed=sensor_seed
        )

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
        self.estimate_sim().add_parameter(sensor_name, parameter_name, parameter)

    def add_old_sliding_estimate_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            window_size: int,
            index: int = 0
    ) -> None:
        parameter: 'SubParameter' = OldSlidingParameter(
            value=value,
            specification=specification,
            window_size=window_size,
            index=index
        )
        self.estimate_sim().add_parameter(sensor_name, parameter_name, parameter)


class PostModel2D(Model2D, ABC):

    def __init__(
            self,
            optimiser: tp.Optional[Optimiser] = None,
            path_seed: tp.Optional[int] = None,
            constraint_seed: tp.Optional[int] = None,
            sensor_seed: tp.Optional[int] = None
    ):
        super().__init__(
            sim_type=PostSubModel2D,
            optimiser=optimiser,
            path_seed=path_seed,
            constraint_seed=constraint_seed,
            sensor_seed=sensor_seed
        )

    def add_spatial_estimate_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            batch_size: int,
            index: int = 0
    ) -> None:
        pass

    def add_variance_analyser(
            self,
            sensor_name: str,
            window_size: int
    ) -> None:
        analyser: 'SubPostAnalyser' = VarianceAnalyser(window_size)
        self.estimate_sim().add_analyser(sensor_name, analyser)

    def post_process(self) -> None:
        assert self.estimate_sim().has_analyser()
        self.estimate_sim().post_process(steps=2)

    def step(self, delta: float) -> None:
        pass
