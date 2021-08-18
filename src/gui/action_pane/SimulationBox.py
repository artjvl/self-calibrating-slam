from PyQt5 import QtWidgets

from src.gui.modules.SimulationHandler import SimulationHandler
from src.simulation.Simulation import Simulation


class SimulationBox(QtWidgets.QComboBox):
    _simulation: SimulationHandler

    # constructor
    def __init__(
            self,
            simulation: SimulationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._simulation = simulation

        # add simulations to combobox
        self._sim_types = [item.value for item in Simulation]
        for sim_type in self._sim_types:
            self.addItem(sim_type.__name__)
        self._simulation.set_simulation(self._sim_types[0])
        self.currentIndexChanged.connect(self._handle_index_change)

    # handlers
    def _handle_index_change(self, index):
        if index >= 0:
            self._simulation.set_simulation(self._sim_types[index])
