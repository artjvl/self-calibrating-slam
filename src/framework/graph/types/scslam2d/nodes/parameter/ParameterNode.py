import typing as tp
from abc import abstractmethod

from src.framework.graph.FactorGraph import FactorNode
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2

SubParameterNode = tp.TypeVar('SubParameterNode', bound='ParameterNode')
T = tp.TypeVar('T')


class ParameterNode(tp.Generic[T], FactorNode[T]):

    def __init__(
            self,
            id_: int = 0,
            value: tp.Optional[T] = None
    ):
        super().__init__(id_, value)
        self._interpretation: tp.Optional[str] = None

    # composition
    @abstractmethod
    def compose_transformation(
            self,
            transformation: SE2,
            inverse: bool = False
    ) -> SE2:
        """
        Composition of a value:
        - inverse = True: add parameter to value
              e.g. convert measurement (= transformation - parameter) to transformation
        - inverse = False: subtract parameter to value
              e.g. convert transformation (= measurement + parameter) to measurement
        """
        pass

    def compose_translation(
            self,
            translation: Vector2,
            inverse: bool = False
    ) -> Vector2:
        transformation: SE2 = SE2.from_translation_angle(translation, 0)
        composed: SE2 = self.compose_transformation(transformation, inverse=inverse)
        return composed.translation()

    # interpretation
    @abstractmethod
    def set_as(self, tag: str) -> None:
        pass

    def set_interpretation(self, tag: str) -> None:
        self._interpretation = tag

    def get_interpretation(self) -> str:
        assert self.has_interpretation()
        return self._interpretation

    def has_interpretation(self) -> bool:
        return self._interpretation is not None

    # read/write
    def read(self, words: tp.List[str]) -> None:
        self.set_as(words[0])
        super().read(words[1:])

    def write(self) -> tp.List[str]:
        return [self.get_interpretation()] + super().write()
