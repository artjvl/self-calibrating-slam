from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.math.lie.transformation import SE2


class NodeSE2(CalibratingNode[SE2]):

    _type = SE2

