from src.framework.graph.types.scslam2d.nodes.InformationNode import InformationNode
from src.framework.structures import Vector3, Square


class InformationNodeV3(InformationNode):
    default_datatype = Vector3

    def get_matrix(self) -> Square:
        vector: Vector3 = self.get_value()
        return Square.from_diagonal(vector.to_list())
