import typing as tp

from src.gui.modules.SimulationHandler import SimulationHandler
from src.gui.utils.GroupComboBox import GroupComboBox, GroupItem
from framework.simulation.Simulation import SubSimulationManager
from src.simulation.simulations import simulations


class SimulationBox(GroupComboBox):
    _sim_handler: SimulationHandler
    _elements: tp.List[tp.Optional['SubSimulationManager']]

    # constructor
    def __init__(
            self,
            sim_handler: SimulationHandler,
            **kwargs
    ):
        super().__init__(**kwargs)

        # attributes
        self._sim_handler = sim_handler
        self._elements = []

        # handlers
        self.currentIndexChanged.connect(self._handle_index_change)

        # actions
        self._construct()
        self.setCurrentIndex(1)

    def _construct(self) -> None:
        self._elements = []

        self.blockSignals(True)
        self.clear()

        section: str
        for section in simulations.sections():
            group: GroupItem = self.add_group(section)
            self._elements.append(None)

            for simulation in simulations.simulations(section):
                group.add_child(simulation.name())
                self._elements.append(simulation)
        self.blockSignals(False)

    # handlers
    def _handle_index_change(self, index):
        if index >= 0:
            simulation: 'SubSimulationManager' = self._elements[index]
            self._sim_handler.set_simulation(simulation)
