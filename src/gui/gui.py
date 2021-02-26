from pyqtgraph.Qt import QtGui

from src.gui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
