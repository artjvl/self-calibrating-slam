from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

from src.gui.action_pane.SelectBox import SelectBox
from src.gui.modules.GraphContainer import GraphContainer
from src.gui.modules.OptimisationHandler import OptimisationHandler


class OptimisationPane(QWidget):

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container = container,
        self._optimisation = OptimisationHandler(container)

        layout = QVBoxLayout()

        self.setLayout(layout)

        # graph optimisation
        select_box: SelectBox = SelectBox(container, self._optimisation, self)
        layout.addWidget(select_box)

        button_optimise = QPushButton(self)
        button_optimise.setText('Optimise graph')
        button_optimise.clicked.connect(self._optimisation.optimise)
        layout.addWidget(button_optimise)
