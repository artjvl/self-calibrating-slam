from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter

from src.gui.action_pane.OptimisationPane import OptimisationPane
from src.gui.action_pane.SimulationPane import SimulationPane
from src.gui.modules.GraphContainer import GraphContainer


class ActionPane(QSplitter):

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setOrientation(Qt.Vertical)
        self.addWidget(SimulationPane(container, self))
        self.addWidget(OptimisationPane(container, self))
