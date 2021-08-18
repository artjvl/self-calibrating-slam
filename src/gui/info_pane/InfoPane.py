import pathlib
import typing as tp

from PyQt5 import QtCore, QtWidgets
from src.framework.graph.Graph import SubGraph
from src.gui.info_pane.BrowserTree import BrowserTree
from src.gui.info_pane.InspectorTree import InspectorTree
from src.gui.info_pane.TimestampBox import TimestampBox
from src.gui.modules.TreeNode import TopTreeNode
from src.gui.utils.LabelPane import LabelPane
from src.gui.utils.PopUp import PopUp
from src.gui.viewer.Viewer import Viewer


class InfoPane(QtWidgets.QWidget):
    _tree: TopTreeNode

    # constructor
    def __init__(
            self,
            tree: TopTreeNode,
            viewer: Viewer,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._tree = tree

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
        button_clear.clicked.connect(self._tree.clear)

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
        timestamp_box = TimestampBox()
        browser = BrowserTree(self._tree, inspector, timestamp_box, viewer, parent=self)

        panels.addWidget(LabelPane(browser, 'Graph browser'))
        panels.addWidget(LabelPane(timestamp_box, 'Select timestamp:'))
        panels.addWidget(LabelPane(inspector, 'Graph-element inspector'))
        layout.addWidget(panels)

        # self.setLayout(layout)
        panels.setSizes([400, 10, 400])
        # panels.setStretchFactor(1, 2)
        # print(self.sizes())

    def handle_load_graph(self) -> None:
        load: tp.Optional[tp.Tuple[SubGraph, pathlib.Path]] = PopUp.load_from_file()
        if load is not None:
            graph: SubGraph
            path: pathlib.Path
            graph, path = load
            self._tree.add_graph(graph, origin=path.name)
