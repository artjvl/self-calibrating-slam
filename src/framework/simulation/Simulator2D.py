import pathlib
from typing import *

import numpy as np

from src.definitions import get_project_root
from src.framework.graph.Graph import Graph, NodeSE2, EdgeSE2
from src.framework.groups import SE2
from src.framework.structures import Vector, Square
from src.utils import GeoHash2D


class Simulator2D(object):

    # constructor
    def __init__(
            self,
            seed: Optional[int] = 0,
            start: Optional[SE2] = None
    ):
        # RNG
        self._rng: Optional[np.random.RandomState] = None
        if seed is not None:
            self._rng = np.random.RandomState(seed)

        # data structures
        self._graph = Graph()
        self._geo: GeoHash2D[NodeSE2] = GeoHash2D()

        # first pose
        self._id_counter = 0
        if start is None:
            start = SE2.from_elements(0, 0, 0)
        self._current = self.add_node(start)
        self._current.set_fixed()

    # simulation methods
    def get_node(self, id: int) -> NodeSE2:
        return self._graph.get_node(id)

    def add_node(
            self,
            pose: SE2
    ) -> NodeSE2:
        translation: Vector = pose.translation()
        x, y = translation.to_tuple()
        node = NodeSE2(self._id_counter, pose)
        self._geo.add(x, y, node)
        self._graph.add_node(node)

        # update for next step
        self._current = node
        self._id_counter += 1

        return node

    def add_edge(
            self,
            a: NodeSE2,
            b: Optional[NodeSE2] = None,
            transformation: Optional[SE2] = None,
            variance: Optional[Vector] = None
    ) -> EdgeSE2:
        if b is None:
            current: NodeSE2 = self._current
            if current.get_id() < a.get_id():
                b = a
                a = current
            else:
                b = current

        if transformation is None:
            transformation: SE2 = b.get_pose() - a.get_pose()
        estimate: SE2 = self._generate_estimate(transformation, variance)

        information: Optional[Square] = None
        if variance is not None:
            information = (1 / variance).to_diagonal()

        edge = EdgeSE2(a, b, estimate, information)
        self._graph.add_edge(edge)

        return edge

    def add_odometry(
            self,
            motion: SE2,
            variance: Optional[Vector] = None
    ) -> Optional[EdgeSE2]:
        estimate: SE2 = self._generate_estimate(motion, variance)

        # pose
        current_node = self._current
        current_pose = current_node.get_pose()
        next_pose: SE2 = current_pose + estimate
        next_node = self.add_node(next_pose)

        # constraint
        edge: EdgeSE2 = self.add_edge(
            current_node,
            transformation=estimate,
            variance=variance
        )
        return edge

    def add_proximity(
            self,
            steps: int,
            transformation: Optional[SE2] = None,
            variance: Optional[Vector] = None
    ) -> Optional[EdgeSE2]:
        node_id = self._id_counter - steps - 1
        if node_id >= 0:
            # assert node_id >= 0

            previous_node: NodeSE2 = self._graph.get_node(node_id)
            edge: EdgeSE2 = self.add_edge(
                previous_node,
                transformation=transformation,
                variance=variance
            )
            return edge
        return None

    def fix_current(self):
        self._current.set_fixed()

    def add_loop_closure(
            self,
            separation: int,
            reach: float,
            transformation: Optional[SE2],
            variance: Optional[Vector]
    ) -> EdgeSE2:
        node: NodeSE2 = self.find_loop_closure(separation, reach)
        edge = self.add_edge(
            node,
            transformation=transformation,
            variance=variance
        )
        return edge

    def find_loop_closure(
            self,
            separation: int,
            reach: float
    ) -> Optional[NodeSE2]:
        current: NodeSE2 = self._current
        neighbours: List[NodeSE2] = self._find_within(current, reach)
        closures: List[NodeSE2] = []
        for neighbour in neighbours:
            if current.get_id() - neighbour.get_id() >= separation:
                closures.append(neighbour)
        if closures:
            return closures[0]
            # return self._rng.choice(closures)
        return None

    # public methods
    def save(self, file: pathlib.Path):
        self._graph.save(file)

    def get_graph(self) -> Graph:
        return self._graph

    # helper-methods
    def _find_within(
            self,
            node: NodeSE2,
            distance: float
    ) -> List[NodeSE2]:
        translation: Vector = node.get_translation()
        x, y = translation.to_tuple()
        return self._geo.find_within(x, y, distance)

    def _generate_estimate(
            self,
            motion: SE2,
            variance: Optional[Vector] = None
    ) -> SE2:
        if variance is not None:
            noise: Vector = self._generate_noise(variance)
            return motion.plus(noise)
        return motion

    def _generate_noise(
            self,
            variance: Vector
    ) -> Vector:
        assert self._rng is not None
        return Vector(variance * self._rng.normal(loc=0, scale=1, size=(3, 1)))
