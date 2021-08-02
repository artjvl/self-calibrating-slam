import typing as tp

from PyQt5 import QtCore
from src.framework.graph.Graph import SubGraph
from src.gui.action_pane.GroupComboBox import GroupItem, GroupComboBox
from src.gui.modules.TreeNode import TopTreeNode, TrajectoryTreeNode, GraphTreeNode
from src.gui.modules.OptimisationHandler import OptimisationHandler


class GraphBox(GroupComboBox):

    signal_update = QtCore.pyqtSignal(int)

    # constructor
    def __init__(
            self,
            tree: TopTreeNode,
            optimisation_handler: OptimisationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._tree = tree
        self._tree.signal_update.connect(self._handle_graph_update)
        self._optimisation_handler = optimisation_handler
        self.currentIndexChanged.connect(self._handle_index_change)

        self._elements: tp.List[tp.Optional[GraphTreeNode]] = []
        # self._current_text: str = ''

    # handlers
    def _handle_graph_update(self, signal: int):
        if signal == self._tree.get_signal_change():
            if self._tree.is_empty():
                self.clear()
            else:
                self._current_text: str = self.currentText()
                self._elements = []

                self.blockSignals(True)
                self.clear()
                trajectory_node: TrajectoryTreeNode
                for trajectory_node in self._tree.get_children():
                    group: GroupItem = self.add_group(trajectory_node.get_gui_name())
                    self._elements.append(None)

                    graph_node: GraphTreeNode
                    for graph_node in trajectory_node.get_children():
                        graph: SubGraph = graph_node.get_graph()
                        if graph.is_perturbed():
                            group.add_child(graph_node.get_gui_name())
                            self._elements.append(graph_node)
                self.setCurrentIndex(-1)
                # index: int = self.findText(self._current_text, QtCore.Qt.MatchFixedString)
                # if index >= 0:
                #     self.setCurrentIndex(index)
                # else:
                self.blockSignals(False)
                self.setCurrentIndex(1)

    def _handle_index_change(self, index):
        graph_node: tp.Optional[GraphTreeNode] = None
        if index >= 0:
            graph_node = self._elements[index]
        self._optimisation_handler.set_graph(graph_node)
