from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSplitter, QPushButton, QSizePolicy

from src.gui.info_pane.BrowserTree import BrowserTree
from src.gui.info_pane.InspectorTree import InspectorTree
from src.gui.modules.GraphContainer import GraphContainer
from src.gui.viewer.Viewer import Viewer


class InfoPane(QSplitter):

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            viewer: Viewer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setOrientation(Qt.Vertical)

        # load-button
        button_load = QPushButton(self)
        button_load.setText('Load file')
        button_load.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred))
        button_load.clicked.connect(container.load_graph)
        self.addWidget(button_load)
        # self.setStretchFactor(0, 0)

        # browser/inspector
        inspector: InspectorTree = InspectorTree(self)
        inspector.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        browser: BrowserTree = BrowserTree(container, inspector, viewer, self)
        browser.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))

        self.addWidget(browser)
        # self.setStretchFactor(1, 1)
        self.addWidget(inspector)
        # self.setStretchFactor(2, 1)
        self.setSizes([20, 400, 400])
        # print(self.sizes())

