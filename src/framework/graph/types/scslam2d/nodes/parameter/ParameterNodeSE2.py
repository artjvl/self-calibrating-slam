from src.framework.graph.types.scslam2d.nodes.parameter.ParameterNode import ParameterNode
from src.framework.math.lie.transformation import SE2


class ParameterNodeSE2(ParameterNode[SE2]):

    _type = SE2
    OFFSET = 'OFFSET'
    BIAS = 'BIAS'

    def set_interpretation(self, tag: str) -> None:
        if tag == self.OFFSET:
            self.set_as_offset()
        elif tag == self.BIAS:
            self.set_as_bias()

    # specific interpretations
    def set_as_offset(self) -> None:
        self._interpretation = self.OFFSET

    def is_offset(self) -> bool:
        return self._interpretation == self.OFFSET

    def set_as_bias(self) -> None:
        self._interpretation = 'BIAS'

    def is_bias(self) -> bool:
        return self._interpretation == self.BIAS

    def compose_transformation(
            self,
            transformation: SE2,
            inverse: bool = False
    ) -> SE2:
        assert self.has_interpretation()
        parameter: SE2 = self.get_value()
        if inverse:
            parameter = parameter.inverse()
        if self._interpretation == self.OFFSET:
            return parameter.inverse() * transformation * parameter
        elif self._interpretation == self.BIAS:
            return transformation * parameter.inverse()
