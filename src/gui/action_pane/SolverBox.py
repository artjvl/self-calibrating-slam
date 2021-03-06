from typing import *

from PyQt5 import QtWidgets, QtCore

from src.gui.modules.OptimisationHandler import OptimisationHandler


class SolverBox(QtWidgets.QComboBox):

    # constructor
    def __init__(
            self,
            optimisation_handler: OptimisationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._optimisation_handler = optimisation_handler
        self._optimisation_handler.signal_update.connect(self._update_box)
        self._update_box()
        self.currentIndexChanged.connect(self._handle_index_change)

    # handlers
    def _handle_index_change(self, index):
        if index >= 0:
            solvers = self._optimisation_handler.get_solvers()
            self._optimisation_handler.set_solver(solvers[index])

    def _update_box(self):
        current_text: str = self.currentText()
        texts: List[str] = [solver.value for solver in self._optimisation_handler.get_solvers()]

        # re-fill ComboBox
        self.blockSignals(True)
        self.clear()
        self.addItems(texts)
        self.setCurrentIndex(-1)
        self.blockSignals(False)

        # select previous item
        index = self.findText(current_text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            self.setCurrentIndex(0)
