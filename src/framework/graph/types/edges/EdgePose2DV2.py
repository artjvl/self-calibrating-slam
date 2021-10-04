import typing as tp

from src.framework.graph.CalibratingGraph import SubCalibratingNode
from src.framework.graph.protocols.Visualisable import DrawEdge
from src.framework.graph.types.edges.CalibratingEdgeV2 import CalibratingEdgeV2
from src.framework.graph.types.nodes.SpatialNode import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square2
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3
from src.gui.viewer.Rgb import RgbTuple, Rgb


class EdgePose2DV2(CalibratingEdgeV2, DrawEdge):
    _num_endpoints = 1

    def __init__(
            self,
            name: tp.Optional[str] = None,
            node: tp.Optional[NodeSE2] = None,
            measurement: tp.Optional[Vector2] = None,
            info_matrix: tp.Optional[Square2] = None
    ):
        nodes: tp.List[SubCalibratingNode] = []
        if node is not None:
            nodes.append(node)
        super().__init__(
            name=name,
            nodes=nodes,
            measurement=measurement,
            info_matrix=info_matrix
        )

    def is_complete(self) -> bool:
        return self.has_value() and len(self.get_endpoints()) == 1

    def get_delta(self) -> Vector2:
        assert self.is_complete()
        node: NodeSE2
        node, = tuple(self.get_endpoints())
        return node.get_value().get_translation()

    # Visualisable
    def draw_nodeset(self) -> tp.Tuple[Vector3, Vector3]:
        pose: SE2 = self.get_endpoints()[0].get_value()
        translation: Vector2 = self.get_delta()
        return pose.translation().to_vector3(), translation.to_vector3()

    @staticmethod
    def draw_rgb() -> RgbTuple:
        return Rgb.GREEN
