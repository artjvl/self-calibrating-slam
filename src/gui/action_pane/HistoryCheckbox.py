from PyQt5 import QtWidgets, QtCore
from src.gui.modules.OptimisationHandler import OptimisationHandler


class HistoryCheckbox(QtWidgets.QCheckBox):

    _optimisation_handler: OptimisationHandler

    def __init__(
            self,
            optimisation_handler: OptimisationHandler,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._optimisation_handler = optimisation_handler
        self.setText('Include history')
        self.setCheckState(
            QtCore.Qt.Checked if self._optimisation_handler.get_include_history() else QtCore.Qt.Unchecked
        )
        self.stateChanged.connect(self._handle_checked)

    def _handle_checked(self):
        self._optimisation_handler.set_include_history(self.checkState() == QtCore.Qt.Checked)