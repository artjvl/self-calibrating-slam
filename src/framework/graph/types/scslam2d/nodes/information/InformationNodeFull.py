import typing as tp

from src.framework.graph.data.Parser import Parser
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import InformationNode
from src.framework.math.matrix.square import SubSquare


class InformationNodeFull(InformationNode):

    def get_matrix(self) -> SubSquare:
        symmetric: tp.List[float] = self.get_value().to_list()
        return Parser.list_to_symmetric(symmetric)

    @classmethod
    def get_length(cls) -> int:
        dim: int = cls.get_dimension()
        return int(dim * (dim + 1) / 2)


class InformationNodeFull2(InformationNodeFull):
    _dim = 2


class InformationNodeFull3(InformationNodeFull):
    _dim = 3
