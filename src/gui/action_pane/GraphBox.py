from typing import *

from PyQt5.QtWidgets import QComboBox

from src.framework.graph import Graph
from src.gui.modules.GraphContainer import GraphContainer
from src.gui.modules.OptimisationHandler import OptimisationHandler


class GraphBox(QComboBox):

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            optimisation: OptimisationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container = container
        self._container.signal_update.connect(self._handle_signal)
        self._optimisation = optimisation
        self.currentIndexChanged.connect(self._handle_index_change)

    # handlers
    def _handle_signal(self, signal: int):
        if signal >= 0:
            self._update_box()

    def _handle_index_change(self, index):
        graphs: List[Graph] = self._container.get_graphs()
        if graphs:
            if index >= 0:
                graph = self._container.get_graphs()[index]
                if graph != self._optimisation.get_graph():
                    self._optimisation.set_graph(graph)
        else:
            self._optimisation.set_graph(None)

    def _update_box(self):
        self.clear()
        for graph in self._container.get_graphs():
            if graph.is_uncertain():
                self.addItem(graph.get_name(short=True))
