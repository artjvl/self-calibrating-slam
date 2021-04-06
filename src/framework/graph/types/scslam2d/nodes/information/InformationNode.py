import typing as tp
from abc import abstractmethod

from src.framework.graph.data import SubDataSquare, DataFactory
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import VectorFactory, SubVector

SubInformationNode = tp.TypeVar('SubInformationNode', bound='InformationNode')


class InformationNode(CalibratingNode):
    _dim: int

    def __init__(
            self,
            id_: int = 0,
            value: tp.Optional[SubVector] = None
    ):
        super().__init__(id_)
        self._value = DataFactory.from_type(
            VectorFactory.from_dim(self.get_length())
        )(value)

    def get_value(self) -> SubVector:
        return self._value

    @abstractmethod
    def get_matrix(self) -> SubSquare:
        pass

    @classmethod
    def get_dimension(cls) -> int:
        return cls._dim

    @classmethod
    @abstractmethod
    def get_length(cls) -> int:
        pass
