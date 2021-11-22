import pathlib
import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.GraphParser import GraphParser
from src.framework.graph.spatial.NodeSE2 import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubGraph


SubPath = tp.TypeVar('SubPath', bound='Path', covariant=True)


class Path(object):

    @abstractmethod
    def next(self) -> SE2:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


class InputPath(Path):
    _path: tp.Optional[pathlib.Path]
    _poses: tp.Optional[tp.List[SE2]]
    _counter: int

    def __init__(self):
        super().__init__()
        self._path = None
        self._poses = None
        self.reset()

    def next(self) -> SE2:
        pose: SE2 = self._poses[self._counter]
        self._counter += 1
        return pose

    def reset(self) -> None:
        if self.has_input_file() and self._poses is None:
            self.load_input_file()
        self._counter = 1

    def has_next(self) -> bool:
        return self._poses is not None and self._counter < len(self._poses)

    def set_input_poses(
            self,
            poses: tp.List[SE2]
    ) -> None:
        self._poses = poses

    def set_input_graph(
            self,
            graph: 'SubGraph'
    ) -> None:
        self._poses = [node.get_value() for node in graph.get_of_type(NodeSE2)]

    def has_input_file(self) -> bool:
        return self._path is not None

    def set_input_file(self, path: pathlib.Path) -> None:
        self._path = path

    def load_input_file(self) -> None:
        assert self.has_input_file()
        self.set_input_graph(GraphParser.load(self._path))


class ManhattanPath(Path):
    _block_size: int
    _step_size: float
    _domain: float
    _step_count: int

    _current: SE2
    _seed: int
    _step_rng: np.random.RandomState
    _sidestep_rng: np.random.RandomState
    _sidesteps_x: tp.List[float]
    _sidesteps_y: tp.List[float]

    def __init__(
            self,
            seed: tp.Optional[int] = None
    ):
        super().__init__()
        self._seed = seed
        self._block_size = 4
        self._step_size = 1.
        self._domain = 50.
        self.reset()

    def reset(self) -> None:
        self._current = SE2.from_translation_angle_elements(0., 0., 0.)
        self._step_count = 0
        self.set_rng(self._seed)
        self._sidesteps_x = []
        self._sidesteps_y = []

    def set_block_size(self, block_size: int) -> None:
        self._block_size = block_size

    def set_step_size(self, step_size: float) -> None:
        self._step_size = step_size

    def set_domain(self, domain: float) -> None:
        self._domain = domain

    def next(self) -> SE2:
        self._step_count += 1
        angle: float = 0.
        if self._step_count == self._block_size:
            angle = self.generate_new_angle()
            self._step_count = 0

        transformation: SE2 = SE2.from_translation_angle_elements(self._step_size, 0., angle)
        new: SE2 = self._current + transformation
        self._current = new
        # return new
        sidestep: np.ndarray = self._sidestep_rng.multivariate_normal(
            mean=[0, 0], cov=0.16 * np.eye(2)
        )
        self._sidesteps_x = [sidestep[0]] + self._sidesteps_x[:3]
        self._sidesteps_y = [sidestep[1]] + self._sidesteps_y[:3]
        return new.oplus(Vector3(np.mean(self._sidesteps_x), np.mean(self._sidesteps_y), 0.))

    def generate_new_angle(self) -> float:
        angle = np.deg2rad(self._step_rng.choice([90., -90.]))
        translation: Vector2 = self._current.translation()
        if np.max(np.abs(translation.array())) > self._domain - self._step_count:
            proposed: SE2 = self._current + \
                            SE2.from_translation_angle_elements(self._step_size, 0., angle) + \
                            SE2.from_translation_angle_elements(self._step_count * self._step_size, 0., 0.)
            if not self.is_in_domain(proposed):
                angle += np.pi
        return angle

    def is_in_domain(self, pose: SE2) -> bool:
        translation: Vector2 = pose.translation()
        return np.max(np.abs(translation.array())) <= self._domain

    def set_rng(self, seed: tp.Optional[int] = None) -> None:
        self._seed = seed
        self._step_rng = np.random.RandomState(seed)
        self._sidestep_rng = np.random.RandomState(seed)
