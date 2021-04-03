from src.framework.graph.types.scslam2d.nodes.ParameterNode import ParameterNode
from src.framework.structures import Vector3


class ParameterNodeV3(ParameterNode):
    default_datatype = Vector3

    def set_interpretation(self, tag: str) -> None:
        if tag == 'SCALE':
            self.set_as_scale()

    def set_as_scale(self) -> None:
        self._interpretation = 'SCALE'
