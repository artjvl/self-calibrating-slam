from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from src.gui.action_pane.OptimisationPane import OptimisationPane
from src.gui.action_pane.SimulationPane import SimulationPane
from src.gui.modules.Container import TopContainer


class ActionPane(QtWidgets.QSplitter):

    # constructor
    def __init__(
            self,
            container: TopContainer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setOrientation(Qt.Vertical)
        self.addWidget(SimulationPane(container, self))
        self.addWidget(OptimisationPane(container, self))
