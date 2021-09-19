import pathlib
import typing as tp
from abc import abstractmethod, ABC

import numpy as np
from framework.graph.GraphParser import GraphParser
from src.framework.graph.types.nodes.SpatialNode import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.simulation.Model2D import SubModel2D

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubGraph
    from src.framework.optimiser.Optimiser import Optimiser
    from src.framework.math.matrix.vector import Vector2

SubSimulation = tp.TypeVar('SubSimulation', bound='Simulation')


class Simulation(object):
    _name: str
    _model: 'SubModel2D'

    def __init__(
            self,
            name: str,
            model: 'SubModel2D'
    ):
        self._name = name
        self._model = model
        self.configure()

    def name(self) -> str:
        """ Returns the name. """
        return self._name

    def set_optimiser(self, optimiser: 'Optimiser'):
        """ Sets the optimiser for the estimate sub-model. """
        self._model.estimate_model().set_optimiser(optimiser)

    def model(self) -> 'SubModel2D':
        """ Returns the model. """
        return self._model

    def reset(self):
        self._model.reset()

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

    def run(self) -> 'SubGraph':
        self.reset()
        self.initialise()
        self.simulate()
        print('\nFinalising...')
        self.finalise()

        self._model.save()
        return self._model.estimate_graph()

    def monte_carlo(
            self,
            num: int
    ) -> tp.List['SubGraph']:
        graphs: tp.List['SubGraph'] = []
        for i in range(num):
            self._model.set_sensor_seed(i)
            estimate = self.run()
            graphs.append(estimate)
        return graphs


class ManhattanSimulation2D(Simulation, ABC):
    _block_size: int
    _step_size: float
    _domain: float
    _step_count: int

    def __init__(
            self,
            name: str,
            model: 'SubModel2D'
    ):
        super().__init__(name, model)
        self._block_size = 4
        self._step_size = 1.
        self._domain = 50.
        self._step_count = 0

    def set_block_size(self, block_size: int) -> None:
        self._block_size = block_size

    def set_step_size(self, step_size: float) -> None:
        self._step_size = step_size

    def set_domain(self, domain: float) -> None:
        self._domain = domain

    def auto_odometry(
            self,
            sensor_name: str
    ) -> None:
        model: 'SubModel2D' = self.model()
        assert model.has_sensor(sensor_name)

        self._step_count += 1
        angle: float = 0.
        if self._step_count == self._block_size:
            angle = self.generate_new_angle()
            self._step_count = 0

        pose: SE2 = SE2.from_translation_angle_elements(self._step_size, 0., angle)
        model.add_odometry(sensor_name, pose)

    def generate_new_angle(self) -> float:
        model: 'SubModel2D' = self.model()

        angle = np.deg2rad(model.get_path_rng().choice([90., -90.]))
        translation: 'Vector2' = model.get_current_pose().translation()
        if np.max(np.abs(translation.array())) > self._domain - self._step_count:
            proposed: SE2 = model.get_current_pose() * \
                            SE2.from_translation_angle_elements(self._step_size, 0., angle) * \
                            SE2.from_translation_angle_elements(self._step_count * self._step_size, 0., 0.)
            if not self.is_in_domain(proposed):
                angle += np.pi
        return angle

    def is_in_domain(self, pose: SE2) -> bool:
        translation: 'Vector2' = pose.translation()
        return np.max(np.abs(translation.array())) <= self._domain


class InputSimulation2D(Simulation, ABC):
    _poses: tp.Optional[tp.List['SE2']]
    _counter: int
    _path: tp.Optional[pathlib.Path]

    def __init__(
            self,
            name: str,
            model: 'SubModel2D'
    ):
        self._path = None
        super().__init__(name, model)
        self._poses = None
        self._counter = 1

    def reset(self) -> None:
        super().reset()
        self._counter = 1

    def has_next(self) -> bool:
        return self._poses is not None and self._counter < len(self._poses)

    def auto_odometry(
            self,
            sensor_name: str
    ) -> None:
        model: 'SubModel2D' = self.model()
        assert model.has_sensor(sensor_name)
        assert self.has_next()

        model.add_odometry_to(sensor_name, self._poses[self._counter])
        self._counter += 1

    def set_input_poses(
            self,
            poses: tp.List['SE2']
    ) -> None:
        self._poses = poses

    def set_input_graph(
            self,
            graph: 'SubGraph'
    ) -> None:
        self._poses = [node.get_value() for node in graph.get_of_type(NodeSE2)]

    def has_path(self) -> bool:
        return self._path is not None

    def set_path(self, path: pathlib.Path) -> None:
        self._path = path

    def load_path(self) -> None:
        assert self.has_path()
        self.set_input_graph(GraphParser.load(self._path))

    def run(self) -> 'SubGraph':
        self.load_path()
        return super().run()
