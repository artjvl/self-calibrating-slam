import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextEdit


class Stream(object):

    # constructor
    def __init__(self, edit: QTextEdit):
        self.edit = edit
        self.out = sys.__stdout__

    # overridden methods
    def write(self, m):
        self.edit.insertPlainText(m)
        self.out.write(m)

    def flush(self):
        pass


class Terminal(QTextEdit):

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QFont('Courier New', 10))
        self.setReadOnly(True)
        sys.stdout = Stream(self)
