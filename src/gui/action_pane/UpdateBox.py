from typing import *

from PyQt5 import QtWidgets, QtCore


class UpdateBox(QtWidgets.QComboBox):

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_text: str = ''

    def before(self):
        self._current_text: str = self.currentText()
        self.blockSignals(True)
        self.clear()

    def after(self):
        self.setCurrentIndex(-1)
        index = self.findText(self._current_text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)
        self.blockSignals(False)

        if index < 0:
            self.setCurrentIndex(0)

    def _update_box(self, texts: List[str]):
        self.before()
        self.addItems(texts)
        self.after()
