from typing import *

from PyQt5 import QtCore

from src.framework.graph import Graph
from src.gui.action_pane.UpdateBox import UpdateBox
from src.gui.modules.GraphContainer import GraphContainer
from src.gui.modules.OptimisationHandler import OptimisationHandler


class GraphBox(UpdateBox):

    signal_update = QtCore.pyqtSignal(int)

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            optimisation_handler: OptimisationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container = container
        self._container.signal_update.connect(self._handle_graph_update)
        self._optimisation_handler = optimisation_handler
        self.currentIndexChanged.connect(self._handle_index_change)

        self._graphs: List[Graph] = []

    # handlers
    def _handle_graph_update(self, signal: int):
        if signal >= 0:
            self._graphs = [graph for graph in self._container.get_graphs() if graph.is_uncertain()]
            self._update_box([graph.get_name(short=True) for graph in self._graphs])

    def _handle_index_change(self, index):
        graphs: List[Graph] = self._container.get_graphs()
        if graphs and index >= 0:
            graph = self._graphs[index]
            if graph != self._optimisation_handler.get_graph():
                self._optimisation_handler.set_graph(graph)
                self.signal_update.emit(0)
        else:
            self._optimisation.set_graph(None)
            self.signal_update.emit(-1)
