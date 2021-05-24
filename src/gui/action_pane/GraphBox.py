import typing as tp

from PyQt5 import QtCore
from src.framework.graph.Graph import SubGraph
from src.gui.action_pane.GroupUpdateComboBox import GroupItem, GroupComboBox
from src.gui.modules.Container import TopContainer, TrajectoryContainer, GraphContainer
from src.gui.modules.OptimisationHandler import OptimisationHandler


class GraphBox(GroupComboBox):

    signal_update = QtCore.pyqtSignal(int)

    # constructor
    def __init__(
            self,
            container: TopContainer,
            optimisation_handler: OptimisationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container = container
        self._container.signal_update.connect(self._handle_graph_update)
        self._optimisation_handler = optimisation_handler
        self.currentIndexChanged.connect(self._handle_index_change)

        self._graph_containers: tp.List[tp.Optional[GraphContainer]] = []
        self._current_text: str = ''

    # handlers
    def _handle_graph_update(self, signal: int):
        if signal >= 0:
            if self._container.is_empty():
                self.clear()
            else:
                self._current_text: str = self.currentText()
                self.blockSignals(True)

                self.clear()
                trajectory_container: TrajectoryContainer
                for trajectory_container in self._container.get_children():
                    group: GroupItem = self.add_group(trajectory_container.get_name())
                    self._graph_containers.append(None)

                    graph_container: GraphContainer
                    for graph_container in trajectory_container.get_children():
                        graph: SubGraph = graph_container.get_graph()
                        if graph.is_perturbed():
                            group.add_child(graph_container.get_name())
                            self._graph_containers.append(graph_container)
                self.setCurrentIndex(-1)
                index: int = self.findText(self._current_text, QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.setCurrentIndex(index)
                else:
                    self.blockSignals(False)
                    self.setCurrentIndex(1)

    def _handle_index_change(self, index):
        graph_container: tp.Optional[GraphContainer] = None
        if index >= 0:
            graph_container = self._graph_containers[index]
        self._optimisation_handler.set_graph(graph_container)
