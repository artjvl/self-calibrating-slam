import typing as tp

from PyQt5 import QtWidgets
from src.gui.modules.TreeNode import GraphTreeNode

if tp.TYPE_CHECKING:
    from src.framework.graph.GraphContainer import SubGraphContainer


class TimestepBox(QtWidgets.QComboBox):

    _node: tp.Optional[GraphTreeNode]  # graph-tree-node that stores the graph(s)
    _elements: tp.List[float]  # list storing all combo-box element-correspondences
    _index: int

    def __init__(
            self
    ):
        super().__init__()
        self._node = None
        self._elements = []
        self._index = 0

        self.currentIndexChanged.connect(self._handle_index_change)
        self.setEnabled(False)

    def set_node(
            self,
            node: GraphTreeNode
    ) -> None:
        if node is not self._node:
            self._node = node
            self.update_contents(node)

    def update_contents(
            self,
            node: 'GraphTreeNode'
    ) -> None:
        graph_container: 'SubGraphContainer' = node.get_graph_container()
        self._index = node.get_index()

        timesteps: tp.List[int] = graph_container.get_timesteps()
        if len(timesteps) > 1:
            texts: tp.List[str] = []

            timestep_set: tp.Set[int] = set()
            timestep_counter: int = 0
            for timestep in timesteps:
                text: str = f'{timestep}'
                if timestep in timestep_set:
                    timestep_counter += 1
                    text += f' (+{timestep_counter})'
                else:
                    timestep_counter = 0
                timestep_set.add(timestep)
                texts.append(text)

            self.blockSignals(True)
            super().clear()
            self.addItems(texts)
            self.setCurrentIndex(self._index)
            self.setEnabled(True)
            self.blockSignals(False)
        else:
            self.clear()

    def clear(self) -> None:
        self.blockSignals(True)
        # self.setCurrentIndex(-1)
        super().clear()
        self.setEnabled(False)
        self.blockSignals(False)

    # handler
    def _handle_index_change(self, index: int) -> None:
        if index != self._index and index >= 0:
            self._index = index
            self._node.set_index(index)
