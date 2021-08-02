import typing as tp

from PyQt5 import QtWidgets
from src.gui.modules.TreeNode import GraphTreeNode


class TimestampBox(QtWidgets.QComboBox):

    _node: tp.Optional[GraphTreeNode]   # graph-tree-node that stores the graph(s)
    _elements: tp.List[float]           # list storing all combo-box element-correspondences
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

    def set_node(self, node: tp.Optional[GraphTreeNode]) -> None:
        if node is not self._node:
            self._node = node
            if node is not None:
                self.update_contents()

    def update_contents(self) -> None:
        assert self._node is not None
        timestamp: tp.Optional[float] = self._node.get_timestamp()

        if timestamp is not None:
            self._elements = self._node.get_timestamps()
            self._index = self._elements.index(timestamp)

            self.blockSignals(True)
            super().clear()
            self.addItems(['{:.3f}'.format(timestamp) for timestamp in self._elements])
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
            self._node.set_timestamp(self._elements[index])
