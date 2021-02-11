from src.framework.graph.base import *


class FactorGraph(BaseGraph):

    # constructor
    def __init__(self):
        super().__init__()

    # public methods
    def compute_error(self) -> float:
        error = 0
        for edge in self.get_nodes():
            error += edge.compute_error()
        return error
