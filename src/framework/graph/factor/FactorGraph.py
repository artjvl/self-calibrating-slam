import warnings
from typing import *

from src.framework.graph.base.BaseGraph import BaseGraph
from src.framework.graph.factor.FactorEdge import FactorEdge
from src.framework.graph.factor.FactorNode import FactorNode


class FactorGraph(BaseGraph[FactorNode, FactorEdge]):

    # constructor
    def __init__(self):
        super().__init__()
        self._dimensionality: Optional[int] = None
        self._is_uncertain: Optional[bool] = None

    # public methods
    def compute_error(self) -> float:
        error = 0
        for edge in self.get_edges():
            error += edge.compute_error()
        return error

    def add_edge(self, edge: FactorEdge) -> None:
        certainty: bool = edge.is_uncertain()
        if self._is_uncertain is None:
            self._is_uncertain = certainty
        elif certainty != self._is_uncertain:
            warnings.warn(
                'Edge {} with certainty {} does not match Graph certainty {}'.format(
                    str(edge), str(certainty), str(self._is_uncertain)
                )
            )

        dimensionality: int = edge.dimensionality
        if dimensionality != self._dimensionality:
            warnings.warn(
                'Edge {} with dimensionality {} does not match Graph dimensionality'.format(
                    str(edge), str(dimensionality), str(self._dimensionality)
                )
            )
        super().add_edge(edge)

    def add_node(self, node: FactorNode) -> None:
        dimensionality: int = node.dimensionality
        if self._dimensionality is None:
            self._dimensionality = dimensionality
        elif dimensionality != self._dimensionality:
            warnings.warn(
                'Dimensionality {} of added node {} is different Graph dimensionality'.format(
                    dimensionality, node, self._dimensionality
                )
            )
        super().add_node(node)

    def get_dimensionality(self) -> Optional[int]:
        return self._dimensionality

    def is_uncertain(self) -> Optional[bool]:
        return self._is_uncertain
