import typing as tp

from src.framework.graph.FactorGraph import FactorNode
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import VectorFactory, SubVector

SubInformationNode = tp.TypeVar('SubInformationNode', bound='InformationNode')


class InformationNode(FactorNode[SubVector]):

    _dim: int

    def get_dim(self) -> int:
        return self._dim

    def get_matrix(self) -> SubSquare:
        diagonal: tp.List[float] = self.get_value().to_list()
        return SquareFactory.from_dim(self.get_dim()).from_diagonal(diagonal)

    @classmethod
    def get_type(cls) -> tp.Type[SubVector]:
        return VectorFactory.from_dim(cls._dim)


class InformationNode2(InformationNode):
    _dim = 2


class InformationNode3(InformationNode):
    _dim = 3
