from PyQt5 import QtWidgets
from src.gui.action_pane.ConfigurationTree import ConfigurationTree
from src.gui.action_pane.SimulationBox import SimulationBox
from src.gui.modules.SimulationHandler import SimulationHandler
from src.gui.modules.TreeNode import TopTreeNode
from src.gui.utils.LabelPane import LabelPane


class SimulationPane(QtWidgets.QWidget):
    _tree: TopTreeNode

    # constructor
    def __init__(
            self,
            tree: TopTreeNode,
            **kwargs
    ):
        super().__init__(**kwargs)

        # attributes
        self._tree = tree
        config = ConfigurationTree(self)
        self._simulation_handler = SimulationHandler(tree, config)

        # layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # graph simulation
        simulator_box = SimulationBox(self._simulation_handler, parent=self)
        layout.addWidget(LabelPane(simulator_box, 'Choose a simulation:'))

        button_simulate = QtWidgets.QPushButton(self)
        button_simulate.setText('Simulate graph')
        button_simulate.clicked.connect(self._simulation_handler.simulate)
        layout.addWidget(button_simulate)

        button_mc = QtWidgets.QPushButton(self)
        button_mc.setText('Monte Carlo simulation')
        button_mc.clicked.connect(self._handle_mc)
        layout.addWidget(button_mc)

        layout.addWidget(LabelPane(config, 'Simulation parameters:'))

    def _handle_mc(self) -> None:
        return self._simulation_handler.monte_carlo(2)
