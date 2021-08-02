from typing import *

from PyQt5.QtCore import QObject, pyqtSignal

from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.gui.action_pane.ParameterTree import ParameterTree
from src.gui.modules.TreeNode import TopTreeNode


class SimulationHandler(QObject):

    signal_update = pyqtSignal(int)

    # constructor
    def __init__(
            self,
            container: TopTreeNode,
            tree: ParameterTree,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container: TopTreeNode = container
        self._tree: ParameterTree = tree
        self._simulation: Optional[BiSimulation2D] = None

    def set_simulation(self, simulation: BiSimulation2D):
        self._simulation = simulation
        if simulation.has_parameters():
            self._tree.construct_tree(simulation.get_parameters())
        else:
            self._tree.clear()

        print(f"gui/SimulationHandler: Simulation '{type(simulation).__name__}' selected")
        self.signal_update.emit(1)

    def get_simulation(self) -> BiSimulation2D:
        return self._simulation

    def simulate(self):
        print(f'gui/SimulationHandler: Simulating trajectory with {type(self._simulation).__name__}...')
        graph_truth, graph_perturbed = self._simulation.simulate()
        self._container.add_graphs(graph_truth, graph_perturbed)
