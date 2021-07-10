import typing as tp

from src.framework.graph.protocols.visualisable.DrawEdge import DrawEdge
from src.framework.graph.types.scslam2d.edges.CalibratingEdgeV2 import CalibratingEdgeV2
from src.framework.graph.types.scslam2d.nodes.NodeSE2 import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square2
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3
from src.gui.viewer.Rgb import RgbTuple, Rgb


class EdgePose2DV2(CalibratingEdgeV2, DrawEdge):
    _num_topological = 1

    def __init__(
            self,
            value: tp.Optional[Vector2] = None,
            info_matrix: tp.Optional[Square2] = None,
            node: tp.Optional[NodeSE2] = None
    ):
        super().__init__(value, info_matrix, node)

    def get_value(self) -> Vector2:
        node: NodeSE2
        node, = tuple(self.get_endpoints())
        return node.get_value().translation()

    # Visualisable
    def draw_nodeset(self) -> tp.Tuple[Vector3, Vector3]:
        pose: SE2 = self.get_endpoints()[0].get_value()
        translation: Vector2 = self.get_value()
        return pose.translation().to_vector3(), translation.to_vector3()

    @staticmethod
    def draw_rgb() -> RgbTuple:
        return Rgb.GREEN
