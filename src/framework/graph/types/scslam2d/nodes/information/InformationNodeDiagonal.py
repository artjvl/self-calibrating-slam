import typing as tp

from src.framework.graph.types.scslam2d.nodes.information.InformationNode import InformationNode
from src.framework.math.matrix.square import SquareFactory, SubSquare


class InformationNodeDiagonal(InformationNode):

    def get_matrix(self) -> SubSquare:
        diagonal: tp.List[float] = self.get_value().to_list()
        return SquareFactory.from_dim(self.get_dimension()).from_diagonal(diagonal)

    def get_length(self):
        return self.get_dimension()


class InformationNodeDiagonal2(InformationNodeDiagonal):
    _dim = 2


class InformationNodeDiagonal3(InformationNodeDiagonal):
    _dim = 3
