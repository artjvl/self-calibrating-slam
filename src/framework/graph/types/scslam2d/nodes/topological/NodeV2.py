from src.framework.graph.FactorGraph import FactorNode
from src.framework.graph.protocols.visualisable.DrawPoint import DrawPoint
from src.framework.math.matrix.vector import Vector2, Vector3


class NodeV2(FactorNode[Vector2], DrawPoint):
    _type = Vector2

    def draw_point(self) -> Vector3:
        return self.get_value().to_vector3()
