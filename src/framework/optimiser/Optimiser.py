from typing import *

from src.framework.graph.Graph import Graph


class Optimiser(object):

    # constructor
    def __init__(self):
        self._graph: Optional[Graph] = None

    # public methods
    def set_graph(self, graph: Optional[Graph]):
        self._graph = graph

    def get_graph(self) -> Optional[Graph]:
        return self._graph
