from typing import *

from src.framework.graph.Graph import Graph
from src.framework.optimiser.Optimiser import Optimiser
from src.gui.modules.GraphContainer import GraphContainer


class OptimisationHandler(object):

    # constructor
    def __init__(
            self,
            container: GraphContainer
    ):
        self._container = container
        self._optimiser = Optimiser()

    def set_graph(self, graph: Optional[Graph]):
        self._optimiser.set_graph(graph)
        print('Selected: {}'.format(graph))

    def get_graph(self) -> Optional[Graph]:
        return self._optimiser.get_graph()

    def optimise(self):
        print('Optimising {}...'.format(self._optimiser.get_graph()))
