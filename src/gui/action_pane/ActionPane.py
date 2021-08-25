from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from src.gui.action_pane.OptimisationPane import OptimisationPane
from src.gui.action_pane.SimulationPane import SimulationPane
from src.gui.modules.TreeNode import TopTreeNode


class ActionPane(QtWidgets.QSplitter):

    # constructor
    def __init__(
            self,
            container: TopTreeNode,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setOrientation(Qt.Vertical)
        self.addWidget(SimulationPane(container, parent=self))
        self.addWidget(OptimisationPane(container, parent=self))
        self.setSizes([800, 200])
