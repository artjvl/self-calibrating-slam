import typing as tp

import numpy as np
from src.framework.graph.Graph import Node
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import VectorFactory, SubVector

SubInformationNode = tp.TypeVar('SubInformationNode', bound='InformationNode')


class InformationNode(Node[SubVector]):

    _dim: int

    def __init__(
            self,
            id_: tp.Optional[int] = None,
            info_diagonal: tp.Optional[SubVector] = None
    ):
        super().__init__(id_)
        self.set_info_diagonal(info_diagonal)

    def set_info_diagonal(self, info_diagonal: SubVector) -> None:
        std: SubVector = self.get_type()(np.sqrt(1 / info_diagonal.array()))
        self.set_value(std)

    def get_info_diagonal(self) -> SubVector:
        std: SubVector = self.get_value()
        return self.get_type()(1 / (std.array()**2))

    def get_cov_diagonal(self) -> SubVector:
        std: SubVector = self.get_value()
        return self.get_type()(std.array()**2)

    def get_dim(self) -> int:
        return self._dim

    def get_info_matrix(self) -> SubSquare:
        return SquareFactory.from_dim(self.get_dim()).from_diagonal(self.get_info_diagonal().to_list())

    def get_cov_matrix(self) -> SubSquare:
        return SquareFactory.from_dim(self.get_dim()).from_diagonal(self.get_cov_diagonal().to_list())

    @classmethod
    def get_type(cls) -> tp.Type[SubVector]:
        return VectorFactory.from_dim(cls._dim)


class InformationNode2(InformationNode):
    _dim = 2


class InformationNode3(InformationNode):
    _dim = 3


class InformationNodeFactory(object):
    _map: tp.Dict[
        int,
        tp.Type[SubInformationNode]
    ] = {
        2: InformationNode2,
        3: InformationNode3
    }

    @classmethod
    def from_dim(cls, dim: int) -> SubInformationNode:
        assert dim in cls._map
        return cls._map[dim]
