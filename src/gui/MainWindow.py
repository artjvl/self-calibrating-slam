from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QDesktopWidget, QSizePolicy, QMenuBar, \
    QStatusBar, QSplitter

from src.gui.action_pane.ActionPane import ActionPane
from src.gui.info_pane.InfoPane import InfoPane
from src.gui.menus import FileMenu, ViewMenu, AboutMenu
from src.gui.modules.Container import ViewerContainer
from src.gui.terminal.TerminalText import TerminalText
from src.gui.viewer.Viewer import Viewer


class MainWindow(QMainWindow):
    # reference: https://memotut.com/create-a-3d-model-viewer-with-pyqt5-and-pyqtgraph-b3916/
    #            https://github.com/Be4rR/STLViewer

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # window
        self.setGeometry(200, 200, 1400, 1000)
        # self.centre()
        self.setWindowTitle('Graph-Viewer')

        # modules
        self._container = ViewerContainer()

        splitter = QSplitter(Qt.Horizontal)

        # terminal
        self._viewer: Viewer = self._init_viewer(splitter, self._container)
        self._menubar: QMenuBar = self._init_menubar(self._container, self._viewer)
        self._statusbar: QStatusBar = self.statusBar()

        # left-layout:
        splitter.addWidget(
            ActionPane(
                self._container
            )
        )
        # centre-layout:
        splitter.addWidget(
            self._init_centre_layout(
                splitter,
                self._viewer
            )
        )
        # right-layout
        splitter.addWidget(
            InfoPane(
                self._container,
                self._viewer
            )
        )
        splitter.setSizes([50, 200, 200])
        self.setCentralWidget(splitter)

        # additional settings
        # self._container.get_graphics_value(Items.AXES.value).set_checked(False)

        # show
        self.show()

    def __del__(self):
        print('Exiting application...')

    # initialisers
    @staticmethod
    def _init_viewer(
            widget: QWidget,
            container: ViewerContainer
    ) -> Viewer:
        # reference: https://pyqtgraph.readthedocs.io/en/latest/
        viewer: Viewer = Viewer(container, widget)
        viewer.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        return viewer

    @staticmethod
    def _init_centre_layout(
            widget: QWidget,
            viewer: Viewer
    ) -> QSplitter:
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(viewer)

        # terminal
        terminal: TerminalText = TerminalText(widget)
        terminal.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
        splitter.addWidget(terminal)
        splitter.setContentsMargins(0, 10, 0, 10)

        splitter.setSizes([400, 100])
        return splitter

    def _init_menubar(
            self,
            container: ViewerContainer,
            viewer: Viewer
    ) -> QMenuBar:
        menubar = self.menuBar()
        menubar.addMenu(FileMenu(container, self))
        menubar.addMenu(ViewMenu(container, viewer, self))
        menubar.addMenu(AboutMenu(self))
        return menubar

    # helper-methods: window
    def centre(self):
        # move frame to centre of screen
        frame_geometry = self.frameGeometry()
        centre = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(centre)
        self.move(frame_geometry.topLeft())
