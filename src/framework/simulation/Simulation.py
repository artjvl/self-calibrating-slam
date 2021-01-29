import numpy as np
from abc import ABC, abstractmethod

from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph import *
from src.framework.graph.types import *


class Simulator(ABC):

    # constructor
    def __init__(self, seed=0):
        self._graph = Graph()
        self._rng = np.random.RandomState(seed)
        self._current_pose = SE2.from_elements(0, 0, 0)
        pose = NodeSE2(0, self._current_pose, self._current_pose)
        self._graph.add_node(pose)

    # public methods
    def current(self):
        return self._current

    def add_odometry(self, motion, variance_vector):
        assert isinstance(motion, SE2)
        assert isinstance(variance_vector, Vector)

        current = self._current_pose
        current_id = current.get_id()

        noise = self.generate_noise(variance_vector)
        next_true = type(self).generate_pose(self._current_pose, motion, 0 * next)
        next_estimated = type(self).generate_pose(self._current_pose, motion, noise)
        next = NodeSE2(current_id + 2, next_true, next_estimated)

        information_matrix = np.diag(1 / variance_vector)
        edge = EdgeSE2(current_id + 1, motion, information_matrix, [current, next])
        self._graph.add_node(next)
        self._graph.add_edge(edge)

    def generate_noise(self, variance_vector):
        assert isinstance(variance_vector, Vector)
        return Vector(variance_vector * self._rng.normal(0, 1, (3, 1)))

    # public static-methods
    @staticmethod
    def generate_pose(start, motion, noise):
        assert isinstance(start, NodeSE2)
        assert isinstance(motion, SE2)
        assert isinstance(noise, Vector)
        next_true = start.get_true() * motion
        next_estimated = start.get_estimated() * motion.plus(noise)
        return NodeSE2(start.get_id() + 1, next_true, next_estimated)

    # abstract methods
    @abstractmethod
    def simulate(self):
        pass
