import typing as tp

from src.framework.graph.data.Parser import Parser
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import InformationNode
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import Vector3, Vector6


class InformationNodeFull(InformationNode):

    def get_matrix(self) -> SubSquare:
        symmetric: tp.List[float] = self.get_value().to_list()
        return Parser.list_to_symmetric(symmetric)

    def get_length(self):
        dim: int = self.get_dimension()
        return dim * (dim + 1) / 2


class InformationNodeFull2(InformationNodeFull):
    _type = Vector3
    _dim = 2


class InformationNodeFull3(InformationNodeFull):
    _type = Vector6
    _dim = 3
