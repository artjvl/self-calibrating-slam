import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.FactorGraph import FactorEdge
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import SubInformationNode
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import SubVector, VectorFactory

SubInformationEdge = tp.TypeVar('SubInformationEdge', bound='InformationEdge')
T = tp.TypeVar('T')


class InformationEdge(FactorEdge[SubVector]):

    _dim: int

    def __init__(
            self,
            minimal_diagonal: tp.Optional[SubVector] = None,
            node: tp.Optional[SubInformationNode] = None
    ):
        assert node.get_dim() == self.get_dim()
        if minimal_diagonal is None:
            minimal_diagonal = VectorFactory.from_dim(self.get_dim()).ones()
        info_matrix: SubSquare = SquareFactory.from_dim(self.get_dim()).from_diagonal(minimal_diagonal)
        super().__init__(None, info_matrix, node)

    def compute_error(self) -> float:
        return float(np.log(super().compute_error()))

    @classmethod
    def get_dim(cls) -> int:
        return cls._dim

    @classmethod
    def get_type(cls) -> tp.Type[SubVector]:
        return VectorFactory.from_dim(cls._dim)

    def get_estimate(self) -> SubVector:
        return self.get_nodes()[0].get_value()

    def compute_error_vector(self) -> SubVector:
        return self.get_estimate()

    def get_cardinality(self) -> int:
        return 1


class InformationEdge2(InformationEdge):
    _dim = 2


class InformationEdge3(InformationEdge):
    _dim = 3


class InformationEdgeFactory(object):
        _map: tp.Dict[int, tp.Type[SubInformationEdge]] = {
            2: InformationEdge2,
            3: InformationEdge3
        }

        @classmethod
        def from_dim(cls, dim: int) -> tp.Type[SubInformationEdge]:
            assert dim in cls._map
            return cls._map[dim]

        @classmethod
        def from_node(
                cls,
                node: SubInformationNode,
                diagonal: tp.Optional[SubVector]
        ) -> SubInformationEdge:
            return cls._map[node.get_dim()](diagonal, node)
