from PyQt5 import QtWidgets

from src.gui.action_pane.ParameterTree import ParameterTree
from src.gui.action_pane.SimulationBox import SimulationBox
from src.gui.modules.Container import ViewerContainer
from src.gui.modules.SimulationHandler import SimulationHandler


class SimulationPane(QtWidgets.QWidget):

    # constructor
    def __init__(
            self,
            container: ViewerContainer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container = container
        tree = ParameterTree(self)
        self._simulation_handler = SimulationHandler(container, tree)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # graph simulation
        simulator_box = SimulationBox(self._simulation_handler, self)
        simulator_box_label = QtWidgets.QLabel(simulator_box)
        simulator_box_label.setText('Choose a simulation:')
        layout.addWidget(simulator_box_label)
        layout.addWidget(simulator_box)

        button_simulate = QtWidgets.QPushButton(self)
        button_simulate.setText('Simulate graph')
        button_simulate.clicked.connect(self._simulation_handler.simulate)
        layout.addWidget(button_simulate)

        tree_label = QtWidgets.QLabel(tree)
        tree_label.setText('Simulation parameters')
        layout.addWidget(tree_label)
        layout.addWidget(tree)
