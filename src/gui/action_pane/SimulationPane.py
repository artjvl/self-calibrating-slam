from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

from src.gui.action_pane.ParameterTree import ParameterTree
from src.gui.action_pane.SimulationBox import SimulationBox
from src.gui.modules.GraphContainer import GraphContainer
from src.gui.modules.SimulationHandler import SimulationHandler


class SimulationPane(QWidget):

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container = container
        self._simulation_handler = SimulationHandler(container)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # graph simulation
        simulator_box: SimulationBox = SimulationBox(self._simulation_handler, self)
        layout.addWidget(simulator_box)

        button_simulate = QPushButton(self)
        button_simulate.setText('Simulate graph')
        button_simulate.clicked.connect(self._simulation_handler.simulate)
        layout.addWidget(button_simulate)

        tree = ParameterTree(self._simulation_handler, self)
        layout.addWidget(tree)
