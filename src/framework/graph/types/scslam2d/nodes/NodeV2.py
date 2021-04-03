from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.structures import Vector2


class NodeSE2(CalibratingNode):
    default_datatype = Vector2
