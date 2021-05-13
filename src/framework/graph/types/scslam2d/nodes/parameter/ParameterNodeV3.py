from src.framework.graph.types.scslam2d.nodes.parameter.ParameterNode import ParameterNode
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector3


class ParameterNodeV3(ParameterNode[Vector3]):

    _type = Vector3
    SCALE = 'SCALE'

    def set_as(self, tag: str) -> None:
        if tag == self.SCALE:
            self.set_as_scale()

    # specific interpretations
    def set_as_scale(self) -> None:
        self._interpretation = self.SCALE

    def is_scale(self) -> bool:
        return self._interpretation == self.SCALE

    def compose_transformation(
            self,
            transformation: SE2,
            inverse: bool = False
    ) -> SE2:
        assert self.has_interpretation()
        parameter: Vector3 = self.get_value()
        if inverse:
            parameter = Vector3(1 / parameter.array())
        if self._interpretation == self.SCALE:
            return SE2.from_matrix(
                Square3.from_diagonal(parameter.to_list()).array() @ transformation.array()
            )
