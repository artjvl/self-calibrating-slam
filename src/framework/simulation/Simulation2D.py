import configparser
from abc import ABC, abstractmethod
from pathlib import Path
from typing import *

import numpy as np

from src.framework.graph.Graph import Graph
from src.framework.graph.types import EdgeSE2, NodeSE2
from src.framework.groups import SE2
from src.framework.simulation.ParameterDictTree import ParameterDictTree
from src.framework.simulation.Simulator2D import Simulator2D
from src.framework.structures import Vector


class Simulation2D(ABC):

    # constructor
    def __init__(
            self,
            seed: Optional[int] = 0
    ):
        self._seed = seed
        self._rng = np.random.RandomState(seed)
        self._true: Optional[Simulator2D] = None
        self._perturbed: Optional[Simulator2D] = None
        self.reset()

        # parameters
        self._parameter_tree = ParameterDictTree()

    def read_parameters(self, base_path: Path):
        # base_path = Path(__file__).parent
        file_path = (base_path / 'config.ini').resolve()
        assert file_path.exists()
        config = configparser.ConfigParser()
        config.read(file_path)

        # initialise new ParameterDictTree
        self._parameter_tree = ParameterDictTree()
        for key, value_string in config['PARAMETERS'].items():
            self._parameter_tree.add_parameter(key, value_string)

    def get_parameters(self) -> Optional[Dict[str, Union[str, int, float, bool]]]:
        return self._parameter_tree.get_parameters()

    def get_parameter_tree(self) -> Optional[ParameterDictTree]:
        return self._parameter_tree

    def simulate(self):
        graphs = self._simulate()
        self.reset()
        return graphs

    def reset(self, seed: Optional[int] = None):
        if seed is None:
            seed = self._seed
        self._seed = seed
        self._true = Simulator2D(seed)
        self._perturbed = Simulator2D(seed)

    # simulation methods
    def add_odometry(
            self,
            motion: SE2,
            variance: Optional[Vector] = None
    ):
        self._true.add_odometry(motion)
        self._perturbed.add_odometry(motion, variance)

    def add_proximity(
            self,
            separation: int,
            variance: Optional[Vector] = None
    ):
        edge: Optional[EdgeSE2] = self._true.add_proximity(separation)
        if edge is not None:
            transformation = edge.get_transformation()
            self._perturbed.add_proximity(separation, transformation, variance)

    def fix_current(self):
        self._true.fix_current()
        self._perturbed.fix_current()

    def add_loop_closure(
            self,
            separation: int,
            reach: float,
            variance: Optional[Vector] = None
    ):
        node: Optional[NodeSE2] = self._true.find_loop_closure(separation, reach)
        if node is not None:
            edge: EdgeSE2 = self._true.add_edge(node)
            print('loop closure: {} - {}'.format(edge.get_node(0).get_id(), edge.get_node(1).get_id()))

            node_perturbed = self._perturbed.get_node(node.get_id())
            self._perturbed.add_edge(
                node_perturbed,
                transformation=edge.get_transformation(),
                variance=variance
            )

    # public methods
    def save(self, name: str):
        self._true.save('{}_true.g2o'.format(name))
        self._perturbed.save('{}_perturbed.g2o'.format(name))

    def get_node_count(self) -> int:
        return len(self._true.get_graph().get_nodes())

    def get_graphs(self) -> Tuple[Graph, Graph]:
        return self.get_true(), self.get_perturbed()

    def get_true(self) -> Graph:
        return self._true.get_graph()

    def get_perturbed(self) -> Graph:
        return self._perturbed.get_graph()

    def get_probability(self) -> float:
        return self._rng.uniform(0, 1)

    # abstract methods
    @abstractmethod
    def _simulate(self):
        pass
