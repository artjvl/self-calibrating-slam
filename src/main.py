from pyqtgraph.Qt import QtGui
from src.definitions import get_project_root

from src.gui.MainWindow import MainWindow

if __name__ == '__main__':
    print(get_project_root())
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
