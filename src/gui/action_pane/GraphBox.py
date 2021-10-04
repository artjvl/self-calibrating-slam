import typing as tp

from src.framework.graph.Graph import SubGraph
from src.gui.modules.OptimisationHandler import OptimisationHandler
from src.gui.modules.TreeNode import TopTreeNode, TrajectoryTreeNode, GraphTreeNode
from src.gui.utils.GroupComboBox import GroupItem, GroupComboBox


class GraphBox(GroupComboBox):

    # constructor
    def __init__(
            self,
            tree: TopTreeNode,
            optimisation_handler: OptimisationHandler,
            **kwargs
    ):
        super().__init__(**kwargs)

        # attributes
        self._tree = tree
        self._optimisation_handler = optimisation_handler
        self._elements: tp.List[tp.Optional[GraphTreeNode]] = []

        # handlers
        self._tree.signal_update.connect(self._handle_tree_update)
        self.currentIndexChanged.connect(self._handle_index_change)

        # actions
        self._construct()
        self.setCurrentIndex(1)

    def _construct(self) -> None:
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
                if not graph.is_consistent():
                    group.add_child(graph_node.get_gui_name())
                    self._elements.append(graph_node)
        self.blockSignals(False)

    # handlers
    def _handle_tree_update(self, signal: int):
        if signal == self._tree.get_signal_change() or signal == self._tree.get_signal_remove():
            if self._tree.is_empty():
                self.clear()
            else:
                self._construct()
                self.setCurrentIndex(1)

    def _handle_index_change(self, index):
        graph_node: tp.Optional[GraphTreeNode] = None
        if index >= 0:
            graph_node = self._elements[index]
        self._optimisation_handler.set_graph(graph_node)
