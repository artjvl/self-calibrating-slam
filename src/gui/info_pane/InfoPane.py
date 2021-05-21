from PyQt5 import QtCore, QtWidgets

from src.framework.graph.Graph import SubGraph
from src.gui.info_pane.BrowserTree import BrowserTree
from src.gui.info_pane.InspectorTree import InspectorTree
from src.gui.info_pane.LabelPane import LabelPane
from src.gui.modules.Container import TopContainer
from src.gui.modules.PopUp import PopUp
from src.gui.viewer.Viewer import Viewer


class InfoPane(QtWidgets.QWidget):

    # constructor
    def __init__(
            self,
            container: TopContainer,
            viewer: Viewer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container = container

        # self.setOrientation(QtCore.Qt.Vertical)
        # self.setContentsMargins(10, 10, 10, 10)

        # vertical layout
        layout = QtWidgets.QVBoxLayout(self)

        # BUTTONS
        # load-button
        button_load = QtWidgets.QPushButton(self)
        button_load.setText('Load file')
        # button_load.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred))
        button_load.clicked.connect(self.handle_load_graph)

        # clear-button
        button_clear = QtWidgets.QPushButton(self)
        button_clear.setText('Clear')
        # button_clear.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred))
        button_clear.clicked.connect(self._container.clear)

        # button layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(button_load)
        button_layout.addWidget(button_clear)
        buttons = QtWidgets.QWidget(self)
        buttons.setLayout(button_layout)
        layout.addWidget(buttons)

        # PANELS
        panels = QtWidgets.QSplitter(self)
        panels.setOrientation(QtCore.Qt.Vertical)
        # panels.setContentsMargins(10, 10, 10, 10)
        # self.setStretchFactor(0, 0)

        inspector = InspectorTree(self)
        browser = BrowserTree(self._container, inspector, viewer, self)

        panels.addWidget(LabelPane(browser, 'Graph browser'))
        panels.addWidget(LabelPane(inspector, 'Graph-element inspector'))
        layout.addWidget(panels)

        # self.setLayout(layout)
        panels.setStretchFactor(0, 2)
        panels.setStretchFactor(1, 2)
        # print(self.sizes())

    def handle_load_graph(self) -> None:
        graph: SubGraph = PopUp.load_from_file()
        if graph is not None:
            self._container.add_graphs(None, graph)
