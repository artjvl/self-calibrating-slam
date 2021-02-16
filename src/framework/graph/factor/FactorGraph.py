from src.framework.graph.base import *
from src.framework.graph.factor.FactorNode import FactorNode
from src.framework.graph.factor.FactorEdge import FactorEdge


class FactorGraph(BaseGraph[FactorNode, FactorEdge]):

    # constructor
    def __init__(self):
        super().__init__()

    # public methods
    def compute_error(self) -> float:
        error = 0
        for edge in self.get_edges():
            error += edge.compute_error()
        return error
