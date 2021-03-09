from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

from src.gui.info_pane.BrowserTree import BrowserTree
from src.gui.info_pane.InspectorTree import InspectorTree
from src.gui.info_pane.LabelPane import LabelPane
from src.gui.modules.GraphContainer import GraphContainer
from src.gui.viewer.Viewer import Viewer


class InfoPane(QtWidgets.QSplitter):

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            viewer: Viewer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setOrientation(Qt.Vertical)
        self.setContentsMargins(10, 10, 10, 10)

        # load-button
        button_load = QtWidgets.QPushButton(self)
        button_load.setText('Load file')
        button_load.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred))
        button_load.clicked.connect(container.load_graph)

        self.addWidget(button_load)
        # self.setStretchFactor(0, 0)

        inspector = InspectorTree(self)
        browser = BrowserTree(container, inspector, viewer, self)

        self.addWidget(LabelPane(browser, 'Graph browser'))
        self.addWidget(LabelPane(inspector, 'Graph-element inspector'))

        self.setSizes([20, 400, 400])
        # print(self.sizes())

