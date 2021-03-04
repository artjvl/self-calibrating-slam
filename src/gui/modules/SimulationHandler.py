from typing import *

from PyQt5.QtCore import QObject, pyqtSignal

from src.framework.simulation.Simulation2D import Simulation2D
from src.gui.modules.GraphContainer import GraphContainer


class SimulationHandler(QObject):

    signal_update = pyqtSignal(int)

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container: GraphContainer = container
        self._simulation: Optional[Simulation2D] = None

    def set_simulation(self, simulation: Simulation2D):
        self._simulation = simulation
        print('Selected: {}'.format(simulation))
        self.signal_update.emit(1)

    def get_simulation(self) -> Simulation2D:
        return self._simulation

    def simulate(self):
        graph_true, graph_perturbed = self._simulation.simulate()
        self._container.add_graph(graph_true)
        self._container.add_graph(graph_perturbed)
