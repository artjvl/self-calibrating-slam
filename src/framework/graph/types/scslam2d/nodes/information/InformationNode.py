import typing as tp
from abc import abstractmethod

from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import VectorFactory, SubVector

SubInformationNode = tp.TypeVar('SubInformationNode', bound='InformationNode')


class InformationNode(CalibratingNode[SubVector]):
    _dim: int

    @abstractmethod
    def get_matrix(self) -> SubSquare:
        pass

    @classmethod
    def get_dimension(cls) -> int:
        return cls._dim

    @classmethod
    def get_type(cls) -> tp.Type[SubVector]:
        return VectorFactory.from_dim(cls.get_length())
