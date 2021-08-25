from PyQt5 import QtWidgets

from src.gui.action_pane.ConfigurationTree import ConfigurationTree
from src.gui.action_pane.SimulationBox import SimulationBox
from src.gui.modules.TreeNode import TopTreeNode
from src.gui.modules.SimulationHandler import SimulationHandler


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
        simulator_box_label = QtWidgets.QLabel(simulator_box)
        simulator_box_label.setText('Choose a simulation:')
        layout.addWidget(simulator_box_label)
        layout.addWidget(simulator_box)

        button_simulate = QtWidgets.QPushButton(self)
        button_simulate.setText('Simulate graph')
        button_simulate.clicked.connect(self._simulation_handler.simulate)
        layout.addWidget(button_simulate)

        tree_label = QtWidgets.QLabel(config)
        tree_label.setText('Simulation parameters')
        layout.addWidget(tree_label)
        layout.addWidget(config)
