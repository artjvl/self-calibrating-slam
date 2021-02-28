from typing import *

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex

from src.gui.modules.SimulationHandler import SimulationHandler


class SimulationTable(QtCore.QAbstractTableModel):

    # constructor
    def __init__(
            self,
            simulation: SimulationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._parameters = simulation.get_simulation().get_parameters()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        keys = self._parameters.keys()
        return len(keys)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 2

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        values = list(self._parameters.items())
        return values[index.row()][index.column()]
