import typing as tp

from src.gui.modules.SimulationHandler import SimulationHandler
from src.gui.utils.GroupComboBox import GroupComboBox, GroupItem
from src.simulation.simulation import simulations, SimType


class SimulationBox(GroupComboBox):
    _sim_handler: SimulationHandler
    _elements: tp.List[tp.Optional[SimType]]

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

            sim_type: SimType
            for sim_type in simulations.list(section):
                group.add_child(sim_type.__name__)
                self._elements.append(sim_type)
        self.blockSignals(False)

    # handlers
    def _handle_index_change(self, index):
        if index >= 0:
            sim_type: SimType = self._elements[index]
            self._sim_handler.set_simulation(sim_type)
