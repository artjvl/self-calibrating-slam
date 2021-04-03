from src.framework.graph.types.scslam2d.nodes.ParameterNode import ParameterNode
from src.framework.groups import SE2


class ParameterNodeSE2(ParameterNode):
    default_datatype = SE2

    def set_interpretation(self, tag: str) -> None:
        if tag == 'OFFSET':
            self.set_as_offset()
        elif tag == 'BIAS':
            self.set_as_bias()

    def set_as_offset(self) -> None:
        self._interpretation = 'OFFSET'

    def set_as_bias(self) -> None:
        self._interpretation = 'BIAS'
