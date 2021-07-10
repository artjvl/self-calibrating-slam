import typing as tp

import numpy as np
from src.framework.graph.Graph import Edge
from src.framework.graph.types.scslam2d.nodes.InformationNode import SubInformationNode
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import SubVector, VectorFactory

SubInformationEdge = tp.TypeVar('SubInformationEdge', bound='InformationEdge')
T = tp.TypeVar('T')


class InformationEdge(Edge[SubVector]):

    _dim: int
    _multiplier: int

    def __init__(
            self,
            info_diagonal: tp.Optional[SubVector] = None,
            node: tp.Optional[SubInformationNode] = None
    ):
        info_matrix: SubSquare = SquareFactory.from_dim(self.get_dim()).identity()
        super().__init__(None, info_matrix, node)
        self.set_info_diagonal(info_diagonal)
        self._multiplier = 0

    def add_node(self, node: SubInformationNode) -> None:
        assert node.get_dim() == self.get_dim()
        super().add_node(node)

    # def compute_error(self) -> float:
    #     return self._multiplier * float(np.log(super().compute_error()))

    @classmethod
    def get_dim(cls) -> int:
        return cls._dim

    @classmethod
    def get_type(cls) -> tp.Type[SubVector]:
        return VectorFactory.from_dim(cls._dim)

    def get_info_node(self) -> SubInformationNode:
        assert self.has_nodes()
        return self.get_nodes()[0]

    def get_estimate(self) -> SubVector:
        return self.get_info_node().get_value()

    def set_info_diagonal(self, info_diagonal: SubVector) -> None:
        std: SubVector = self.get_type()(np.sqrt(1 / info_diagonal.array()))
        self.set_measurement(std)

    def get_info_diagonal(self) -> SubVector:
        std: SubVector = self.get_measurement()
        return self.get_type()(1 / (std.array()**2))

    def get_cov_diagonal(self) -> SubVector:
        std: SubVector = self.get_measurement()
        return self.get_type()(std.array()**2)

    # def compute_error_vector(self) -> SubVector:
    #     return self.get_estimate()

    @staticmethod
    def f_error(error) -> float:
        return np.log(error) + 1/(100 * error**100) - 0.01

    def compute_error_vector(self) -> SubVector:
        cov_diagonal: SubVector = self.get_info_node().get_cov_diagonal()
        min_cov_diagonal: SubVector = self.get_cov_diagonal()

        ratios: tp.List[float] = []
        dot: float = 0.
        determinant: float = 1.
        for i in range(self.get_dim()):
            ratio = cov_diagonal[i] / min_cov_diagonal[i]
            ratios.append(ratio)
            dot += ratio
            determinant *= ratio

        scaled_ratios: SubVector = self.get_type()(
            [self._multiplier * self.f_error(determinant) * (ratio/dot) for ratio in ratios]
        )
        return self.get_type()(np.sqrt(scaled_ratios.array()))

    def get_cardinality(self) -> int:
        return 1

    def increment_multiplier(self) -> None:
        self._multiplier += 1

    # read/write
    def read(self, words: tp.List[str]) -> None:
        self._multiplier = int(words[0])
        words = self._measurement.read_rest(words[1:])
        assert not words, f"Words '{words}' are left unread."

    def write(self) -> tp.List[str]:
        words: tp.List[str] = [str(self._multiplier)] + self._measurement.write()
        return words


class InformationEdge2(InformationEdge):
    _dim = 2


class InformationEdge3(InformationEdge):
    _dim = 3


class InformationEdgeFactory(object):
        _map: tp.Dict[int, tp.Type[SubInformationEdge]] = {
            2: InformationEdge2,
            3: InformationEdge3
        }

        @classmethod
        def from_dim(cls, dim: int) -> tp.Type[SubInformationEdge]:
            assert dim in cls._map
            return cls._map[dim]

        @classmethod
        def from_node(
                cls,
                node: SubInformationNode,
                diagonal: tp.Optional[SubVector]
        ) -> SubInformationEdge:
            return cls._map[node.get_dim()](diagonal, node)
