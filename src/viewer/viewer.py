from pyqtgraph.Qt import QtGui

from src.viewer.GraphViewer import GraphViewer


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = GraphViewer()
    window.show()
    app.exec_()
