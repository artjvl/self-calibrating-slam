from typing import *

from PyQt5.QtCore import QObject, pyqtSignal

from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.gui.action_pane.ParameterTree import ParameterTree
from src.gui.modules.Container import ViewerContainer


class SimulationHandler(QObject):

    signal_update = pyqtSignal(int)

    # constructor
    def __init__(
            self,
            container: ViewerContainer,
            tree: ParameterTree,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container: ViewerContainer = container
        self._tree: ParameterTree = tree
        self._simulation: Optional[BiSimulation2D] = None

    def set_simulation(self, simulation: BiSimulation2D):
        self._simulation = simulation
        if simulation.has_parameters():
            self._tree.construct_tree(simulation.get_parameters())
        else:
            self._tree.clear()

        print("Simulation '{}' selected".format(type(simulation).__name__))
        self.signal_update.emit(1)

    def get_simulation(self) -> BiSimulation2D:
        return self._simulation

    def simulate(self):
        graph_true, graph_perturbed = self._simulation.simulate()
        self._container.add_graph(graph_true)
        self._container.add_graph(graph_perturbed)
