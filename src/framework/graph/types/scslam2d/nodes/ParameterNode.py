import typing as tp
from abc import abstractmethod

from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode

SubParamNode = tp.TypeVar('SubParamNode', bound='ParameterNode')


class ParameterNode(CalibratingNode):

    def __init__(
            self,
            id_: int = 0
    ):
        super().__init__(id_)
        self._interpretation: tp.Optional[str] = None

    @abstractmethod
    def set_interpretation(self, tag: str) -> None:
        pass

    def get_interpretation(self) -> str:
        assert self._interpretation is not None
        return self._interpretation

    def read(self, words: tp.List[str]) -> None:
        self.set_interpretation(words[0])
        super().read(words[1:])

    def write(self) -> tp.List[str]:
        return [self.get_interpretation()] + super().write()
