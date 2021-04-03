from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.groups import SE2


class NodeSE2(CalibratingNode):
    default_datatype = SE2
