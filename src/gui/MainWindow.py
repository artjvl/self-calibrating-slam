from PyQt5.QtWidgets import QMainWindow, QWidget, QDesktopWidget, QHBoxLayout, QSizePolicy, QVBoxLayout, QMenuBar, \
    QPushButton, QStatusBar

from src.gui.GraphContainer import GraphContainer
from src.gui.menus import FileMenu, ViewMenu, AboutMenu
from src.gui.viewer.Viewer import Viewer
from src.gui.widgets import Browser, Inspector, Terminal


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

        # initialise central widget
        central_widget = QWidget(self)

        # initialise data structure (i.e., Graph-Container)
        self._container: GraphContainer = GraphContainer()

        # initialise viewer widget
        self._viewer: Viewer = self._init_viewer(central_widget, self._container)

        # initialise menu-bar
        self._menubar: QMenuBar = self._init_menubar(self._container, self._viewer)

        # initialise info-sidebar
        self._inspector: Inspector = self._init_inspector(central_widget)
        self._browser: Browser = self._init_browser(central_widget, self._container, self._inspector, self._viewer)

        self._statusbar: QStatusBar = self.statusBar()

        # widgets:
        self._terminal = self._init_terminal(central_widget)
        # right:
        self._load = self._init_load(central_widget)

        # layout
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        # left-layout:
        left_layout = QVBoxLayout()
        left_layout.addWidget(self._viewer)
        left_layout.addWidget(self._terminal)
        layout.addLayout(left_layout)
        # right-layout:
        right_layout = QVBoxLayout()
        right_layout.addWidget(self._load)
        right_layout.addWidget(self._browser)
        right_layout.addWidget(self._inspector)
        layout.addLayout(right_layout)

        # show
        self.show()

    def __del__(self):
        print('Exiting application...')

    # initialisers
    @staticmethod
    def _init_viewer(
            widget: QWidget,
            container: GraphContainer
    ) -> Viewer:
        # reference: https://pyqtgraph.readthedocs.io/en/latest/
        viewer: Viewer = Viewer(container, widget)
        viewer.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        return viewer

    @staticmethod
    def _init_browser(
            widget: QWidget,
            container: GraphContainer,
            inspector: Inspector,
            viewer: Viewer
    ) -> Browser:
        browser: Browser = Browser(container, inspector, viewer, widget)
        browser.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        return browser

    @staticmethod
    def _init_inspector(
            widget: QWidget
    ) -> Inspector:
        inspector: Inspector = Inspector(widget)
        inspector.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        return inspector

    @staticmethod
    def _init_terminal(widget: QWidget) -> Terminal:
        terminal: Terminal = Terminal(widget)
        terminal.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
        return terminal

    def _init_load(self, widget) -> QPushButton:
        button_load = QPushButton(widget)
        button_load.setText('Load file')
        button_load.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        button_load.clicked.connect(self._container.add_graph)
        return button_load

    def _init_menubar(
            self,
            container: GraphContainer,
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
