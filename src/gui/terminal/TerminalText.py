import sys

from PyQt5 import QtGui, QtWidgets


class Stream(object):

    # constructor
    def __init__(self, edit: QtWidgets.QTextEdit):
        self.edit = edit
        self.out = sys.__stdout__

    # overridden methods
    def write(self, m):
        self.edit.insertPlainText(m)
        self.out.write(m)

    def flush(self):
        pass


class TerminalText(QtWidgets.QTextEdit):

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QtGui.QFont('Courier New', 8))
        self.setReadOnly(True)
        p = self.palette()
        p.setColor(QtGui.QPalette.Base, QtGui.QColor("#2C2C2C"))
        p.setColor(QtGui.QPalette.Text, QtGui.QColor("#ffffff"))
        self.setPalette(p)

        sys.stdout = Stream(self)

    def insertPlainText(self, text: str) -> None:
        super().insertPlainText(text)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
