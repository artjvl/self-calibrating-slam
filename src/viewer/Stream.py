import sys

from PyQt5.QtWidgets import QTextEdit


# class Stream(QObject):
#     handler = pyqtSignal(str)
#
#     def write(self, text):
#         # self.handler.emit(str(text))
#         try:
#             self.handler.emit(str(text))
#         finally:
#             # sys.stdout = sys.__stdout__
#             self.write('pass')
#
#     def __del__(self):
#         print('Exiting stream')


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
