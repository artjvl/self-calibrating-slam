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
            optimisation: OptimisationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container = container
        self._container.signal_update.connect(self._handle_graph_update)
        self._optimisation = optimisation
        self.currentIndexChanged.connect(self._handle_index_change)

    # helper-methods
    def _get_texts(self) -> List[str]:
        return [graph.get_name(short=True) for graph in self._container.get_graphs() if graph.is_uncertain()]

    # handlers
    def _handle_graph_update(self, signal: int):
        if signal >= 0:
            self._update_box(self._get_texts())

    def _handle_index_change(self, index):
        graphs: List[Graph] = self._container.get_graphs()
        if graphs and index >= 0:
            graph = self._container.get_graphs()[index]
            if graph != self._optimisation.get_graph():
                self._optimisation.set_graph(graph)
                self.signal_update.emit(0)
        else:
            self._optimisation.set_graph(None)
            self.signal_update.emit(-1)
