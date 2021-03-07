from typing import *

from PyQt5 import QtWidgets, QtCore


class UpdateBox(QtWidgets.QComboBox):

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _update_box(self, texts: List[str]):
        current_text: str = self.currentText()

        # re-fill ComboBox
        self.blockSignals(True)
        self.clear()
        self.addItems(texts)
        self.setCurrentIndex(-1)

        # select previous item
        index = self.findText(current_text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)
        self.blockSignals(False)

        if index < 0:
            self.setCurrentIndex(0)
