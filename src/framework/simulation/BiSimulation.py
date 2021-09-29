import pathlib
import sys
import typing as tp
from abc import abstractmethod
from datetime import datetime

import numpy as np
from src.framework.graph.GraphParser import GraphParser
from src.framework.simulation.Sensor import SensorFactory
from src.framework.simulation.Simulation import PlainSimulation, OptimisingSimulation, PostSimulation
from src.utils import GeoHash2D

if tp.TYPE_CHECKING:
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.Graph import SubEdge, SubGraph
    from src.framework.graph.types.nodes.SpatialNode import NodeSE2
    from src.framework.math.lie.transformation import SE2
    from src.framework.math.matrix.square import SubSquare
    from src.framework.math.matrix.vector import Vector2
    from src.framework.optimiser.Optimiser import Optimiser
    from src.framework.simulation.Path import SubPath
    from src.framework.simulation.Sensor import SubSensor
    from src.framework.simulation.Simulation import SubSimulation

SubBiSimulation = tp.TypeVar('SubBiSimulation', bound='BiSimulation')


class BiSimulation(object):
    _name: str
    _geo: GeoHash2D[int]
    _path: tp.Optional['SubPath']

    # optimiser
    _optimiser: tp.Optional['Optimiser']

    # rng
    _constraint_seed: tp.Optional[int]
    _constraint_rng: np.random.RandomState
    _sensor_seed: tp.Optional[int]

    # simulations
    _truth_sim: tp.Optional['SubSimulation']
    _estimate_sim: tp.Optional['SubSimulation']

    # config
    _config: tp.Union[int, str]

    def __init__(
            self,
            name: tp.Optional[str] = None,
            optimiser: tp.Optional['Optimiser'] = None
    ):
        super().__init__()
        if name is None:
            name = self.__class__.__name__
        self._name = name
        self._optimiser = optimiser
        self._geo = GeoHash2D[int]()
        self._path = None

        # rng
        self.set_constraint_rng(None)
        self._sensor_seed = None

        # simulations
        self._truth_sim = None
        self._estimate_sim = None

        # config
        self._config = 0
        self.configure()

    # name
    def set_name(self, name: str) -> None:
        self._name = name

    def get_name(self) -> str:
        """ Returns the name. """
        return self._name

    # optimiser
    def set_optimiser(self, optimiser: 'Optimiser') -> None:
        self._optimiser = optimiser

    # simulations
    def has_simulations(self) -> bool:
        return self._truth_sim is not None and self._estimate_sim is not None

    def truth_simulation(self) -> 'SubSimulation':
        assert self.has_simulations()
        return self._truth_sim

    def estimate_simulation(self) -> 'SubSimulation':
        assert self.has_simulations()
        return self._estimate_sim

    def reset(self) -> None:
        if self.has_path():
            self._path.reset()

        truth_sim: 'SubSimulation' = self.truth_simulation()
        estimate_sim: 'SubSimulation' = self.estimate_simulation()

        # reset simulations
        truth_sim.reset()
        estimate_sim.reset()
        estimate_sim.graph().assign_truth(truth_sim.graph())

        # geo
        self._geo.reset()
        translation: 'Vector2' = truth_sim.current().get_value().translation()
        self._geo.add(translation[0], translation[1], self.get_current_id())
        self.set_constraint_rng(self._constraint_seed)

    def set_config(self, config: tp.Union[int, str]) -> None:
        self._config = config

    def get_config(self) -> tp.Union[int, str]:
        return self._config

    # path
    def set_path(self, path: 'SubPath') -> None:
        self._path = path

    def has_path(self) -> bool:
        return self._path is not None

    def path(self) -> 'SubPath':
        assert self.has_path()
        return self._path

    # current
    def get_current_node(self) -> 'NodeSE2':
        return self.truth_simulation().current()

    def get_current_pose(self) -> 'SE2':
        return self.get_current_node().get_value()

    def get_current_id(self) -> int:
        """ Returns the synchronised id of the current pose-node. """
        return self.get_current_node().get_id()

    def align_ids(self) -> None:
        """ Aligns the current-pose-id of each simulation. """

        truth_sim: 'SubSimulation' = self.truth_simulation()
        estimate_sim: 'SubSimulation' = self.estimate_simulation()
        id_: int = max(truth_sim.get_id(), estimate_sim.get_id())
        truth_sim.set_count(id_)
        estimate_sim.set_count(id_)

    def timestep(self) -> float:
        return self.truth_simulation().get_timestep()

    # edges
    def add_edge(
            self,
            sensor_name: str,
            ids: tp.List[int],
            value: 'Quantity'
    ) -> None:
        """ Adds a new edge between <ids> with <value>, as measured by <sensor_name>. """

        truth_sim: 'SubSimulation' = self.truth_simulation()
        estimate_sim: 'SubSimulation' = self.estimate_simulation()
        self.align_ids()

        # add new 'truth' edge
        truth_sensor: 'SubSensor' = truth_sim.model().get_sensor(sensor_name)
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

        truth_sim: 'SubSimulation' = self.truth_simulation()
        transformation: 'SE2' = truth_sim.get_node(to_id).get_value() - truth_sim.get_node(from_id).get_value()
        self.add_edge(sensor_name, [from_id, to_id], transformation)

    # odometry
    def add_odometry(
            self,
            sensor_name: str,
            transformation: 'SE2'
    ) -> None:
        """ Adds a new pose-node and edge with <transformation>, as measured by <sensor_name>. """

        self.align_ids()
        truth_sim: 'SubSimulation' = self.truth_simulation()
        estimate_sim: 'SubSimulation' = self.estimate_simulation()

        # add new 'truth' pose and edge
        truth_sensor: 'SubSensor' = truth_sim.model().get_sensor(sensor_name)
        truth_measurement: 'SE2' = truth_sensor.decompose(transformation)
        truth_node, truth_edge = truth_sim.add_odometry(sensor_name, truth_measurement)

        # store new 'truth' pose in geo-hashmap
        translation: 'Vector2' = truth_sim.current().get_value().translation()
        self._geo.add(translation[0], translation[1], truth_sim.current().get_id())

        # add new 'perturbed' pose and edge
        estimate_measurement: 'SE2' = truth_sensor.measure(truth_measurement)
        estimate_node, estimate_edge = estimate_sim.add_odometry(sensor_name, estimate_measurement)
        estimate_node.assign_truth(truth_node)
        estimate_edge.assign_truth(truth_edge)

    def add_odometry_to(
            self,
            sensor_name: str,
            pose: 'SE2'
    ) -> None:
        """ Adds a new pose-node and edge at <pose>, as measured by <sensor_name>. """
        transformation: 'SE2' = pose - self.get_current_pose()
        self.add_odometry(sensor_name, transformation)

    def auto_odometry(
            self,
            sensor_name: str
    ) -> None:
        assert self.has_path()
        pose: 'SE2' = self._path.next()
        self.add_odometry_to(sensor_name, pose)

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

        truth_sim: 'SubSimulation' = self.truth_simulation()

        pose_ids: tp.List[int] = truth_sim.pose_ids()
        if len(pose_ids) > separation:
            current: 'NodeSE2' = truth_sim.current()
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

        truth_sim: 'SubSimulation' = self.truth_simulation()

        pose_ids: tp.List[int] = truth_sim.pose_ids()
        if len(pose_ids) > steps:
            current_id: int = truth_sim.current().get_id()
            proximity_id: int = pose_ids[-1 - steps]
            self.add_poses_edge(sensor_name, proximity_id, current_id)

    # rng
    def set_constraint_rng(self, seed: tp.Optional[int] = None) -> None:
        self._constraint_seed = seed
        self._constraint_rng = np.random.RandomState(seed)

    def get_constraint_rng(self) -> np.random.RandomState:
        return self._constraint_rng

    def set_sensor_seed(self, seed: tp.Optional[int] = None) -> None:
        self._sensor_seed = seed

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
        self.truth_simulation().model().add_sensor(
            sensor_name, SensorFactory.from_value(
                type_,
                info_matrix=info_matrix_truth,
                seed=self._sensor_seed
            )
        )
        self.estimate_simulation().model().add_sensor(
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
        return self.truth_simulation().model().has_sensor(sensor_name)

    def get_truth_sensor(self, sensor_name: str) -> 'SubSensor':
        return self.truth_simulation().model().get_sensor(sensor_name)

    def get_estimate_sensor(self, sensor_name: str) -> 'SubSensor':
        return self.estimate_simulation().model().get_sensor(sensor_name)

    def set_truth_info_matrix(self, sensor_name: str, info_matrix: 'SubSquare') -> None:
        self.get_truth_sensor(sensor_name).set_info_matrix(info_matrix)

    def set_truth_cov_matrix(self, sensor_name: str, cov_matrix: 'SubSquare') -> None:
        self.get_truth_sensor(sensor_name).set_cov_matrix(cov_matrix)

    def get_sensors(self, sensor_name: str) -> tp.Tuple['SubSensor', 'SubSensor']:
        return self.get_truth_sensor(sensor_name), self.get_estimate_sensor(sensor_name)

    # tools
    @staticmethod
    def print(text: str) -> None:
        sys.__stdout__.write(f'\r{text}')
        sys.__stdout__.flush()

    def save(
            self,
            name: tp.Optional[str] = None,
            folder: tp.Optional[pathlib.Path] = None,
            should_print: bool = False
    ) -> None:
        if folder is None:
            folder: str = 'graphs/simulation'
        if name is None:
            name = datetime.now().strftime('%Y%m%d-%H%M%S')

        GraphParser.save_path_folder(self.truth_simulation().graph(), folder, name=f'{name}_truth', should_print=should_print)
        GraphParser.save_path_folder(self.estimate_simulation().graph(), folder, name=f'{name}_perturbed', should_print=should_print)

    # simulation
    def step(self) -> None:
        self.truth_simulation().step()
        self.estimate_simulation().step()
        self.print(f'framework/Simulation: Time: {self.timestep():.2f}')

    def run(self, should_save: bool = False) -> 'SubGraph':
        self.reset()
        self.initialise()
        self.simulate()
        print('\nframework/Simulation: Finalising simulation...')
        self.finalise()

        if should_save:
            self.save()
        return self.estimate_simulation().graph()

    def monte_carlo(
            self,
            num: int
    ) -> tp.List['SubGraph']:
        graphs: tp.List['SubGraph'] = []
        for i in range(num):
            self.set_sensor_seed(i)
            print(f'framework/Simulation: Monte Carlo step {i + 1}/{num}...')
            estimate = self.run()
            graphs.append(estimate)
        return graphs

    # simulation
    def set_simulation(self, simulation: tp.Type['SubSimulation']) -> 'SubSimulation':
        self._truth_sim = PlainSimulation()
        self._estimate_sim = simulation(optimiser=self._optimiser)
        return self._estimate_sim

    def set_plain_simulation(self) -> PlainSimulation:
        return self.set_simulation(PlainSimulation)

    def set_optimising_simulation(self) -> OptimisingSimulation:
        return self.set_simulation(OptimisingSimulation)

    def set_post_simulation(self) -> PostSimulation:
        return self.set_simulation(PostSimulation)

    @abstractmethod
    def configure(self) -> None:
        pass

    @abstractmethod
    def initialise(self) -> None:
        pass

    @abstractmethod
    def simulate(self) -> None:
        pass

    @abstractmethod
    def finalise(self) -> None:
        pass

