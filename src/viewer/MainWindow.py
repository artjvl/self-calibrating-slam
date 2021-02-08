import pathlib

from PyQt5.QtCore import *  # QSize
from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout
from PyQt5.QtGui import *  # QDesktopServices

import pyqtgraph.opengl as gl

from src.framework.graph import *

from src.viewer.Browser import Browser
from src.viewer.Inspector import Inspector
from src.viewer.Viewer import Viewer


class MainWindow(QMainWindow):
    # reference: https://memotut.com/create-a-3d-model-viewer-with-pyqt5-and-pyqtgraph-b3916/
    #            https://github.com/Be4rR/STLViewer

    # constructor
    def __init__(self):
        super(MainWindow, self).__init__()
        self._graphs = []

        # window
        self.setGeometry(200, 200, 1000, 800)
        # self.centre()
        self.setWindowTitle('Graph-Viewer')

        # widgets:
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        # left:
        self.viewer = self.init_viewer(self.central_widget)
        self.terminal = self.init_terminal(self.central_widget)
        # right:
        self.load = self.init_load(self.central_widget)
        self.inspector = self.init_inspector(self.central_widget)
        self.browser = self.init_browser(self.inspector, self.central_widget)

        # window:
        self.menubar = self.init_menubar(self, self.viewer)
        self.statusbar = self.statusBar()

        # layout
        self.layout = QHBoxLayout(self.central_widget)
        # left-layout:
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.viewer)
        self.left_layout.addWidget(self.terminal)
        self.layout.addLayout(self.left_layout)
        # right-layout:
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.load)
        self.right_layout.addWidget(self.browser)
        self.right_layout.addWidget(self.inspector)
        self.layout.addLayout(self.right_layout)

        # show
        self.show()
        # self.add_line()

    # widgets
    def init_viewer(self, widget) -> Viewer:
        assert isinstance(widget, QWidget)
        # reference: https://pyqtgraph.readthedocs.io/en/latest/
        viewer = Viewer(widget)
        viewer.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        return viewer

    def init_terminal(self, widget) -> QTextEdit:
        terminal = QTextEdit(widget)
        terminal.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
        terminal.setFont(QFont('Courier New', 10))
        return terminal

    def init_load(self, widget) -> QPushButton:
        button_load = QPushButton(widget)
        button_load.setText('Load file')
        button_load.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        button_load.clicked.connect(self.handle_load)
        return button_load

    def init_menubar(self, window, viewer) -> QMenuBar:
        assert isinstance(window, QMainWindow)
        assert isinstance(viewer, Viewer)

        menubar = self.menuBar()

        # file-menu
        menu_file = menubar.addMenu('&File')
        menu_file.setToolTipsVisible(True)

        # file: load
        action_file_load = self.create_action(window, '&Load', 'Load a file', self.handle_load)
        action_file_load.setShortcut('Ctrl+L')
        menu_file.addAction(action_file_load)

        # file: (separator)
        menu_file.addSeparator()

        # file: exit

        action_file_exit = self.create_action(window, '&Quit', 'Exit application', self.handle_quit)
        action_file_exit.setShortcut('Ctrl+Q')
        menu_file.addAction(action_file_exit)

        # view-menu
        menu_view = menubar.addMenu('&View')
        menu_view.setToolTipsVisible(True)

        # view: grid
        action_view_grid = self.create_action(window, '&Grid', 'Show/hide grid', self.handle_toggle_grid)
        action_view_grid.setCheckable(True)
        action_view_grid.setChecked(viewer.is_grid())
        menu_view.addAction(action_view_grid)

        # view: (separator)
        menu_view.addSeparator()

        # view: top
        action_view_top = self.create_action(window, '&Top', 'Move camera to top view', self.handle_top)
        menu_view.addAction(action_view_top)

        # view: isometric
        action_view_isometric = self.create_action(window, '&Isometric', 'Move camera to isometric view', self.handle_isometric)
        menu_view.addAction(action_view_isometric)

        # about-menu
        menu_about = menubar.addMenu('&About')
        menu_about.setToolTipsVisible(True)

        # about: GitHub
        url = QUrl('https://github.com/artjvl/self-calibrating-slam')
        action_about_github = self.create_action(window, 'Go to GitHub', 'Redirect to source-code on GitHub', lambda: QDesktopServices.openUrl(url))
        menu_about.addAction(action_about_github)

        return menubar

    def init_browser(self, inspector, widget) -> Browser:
        assert isinstance(inspector, Inspector)
        assert isinstance(widget, QWidget)
        browser = Browser(inspector, widget)
        browser.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        return browser

    def init_inspector(self, widget) -> Inspector:
        assert isinstance(widget, QWidget)
        properties = Inspector(widget)
        properties.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        return properties

    # actions
    def handle_load(self):
        print("Loading file...")
        # path = Path().absolute()
        file_name = QFileDialog.getOpenFileName(self, 'Select file', '', 'g2o (*.g2o)')
        if file_name[0]:
            self.load_file(file_name[0])
        # self.load_file()

    def handle_quit(self):
        print('Exiting application...')
        qApp.quit()

    def handle_toggle_grid(self):
        self.viewer.set_grid(not self.viewer.is_grid())

    def handle_top(self):
        print(self.viewer.cameraPosition())
        print('Moved camera to top view')

    def handle_isometric(self):
        print(self.viewer.cameraPosition())
        print('Moved camera to isometric view')

    # helper-methods: window
    def centre(self):
        # move frame to centre of screen
        frame_geometry = self.frameGeometry()
        centre = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(centre)
        self.move(frame_geometry.topLeft())

    # helper-methods: menubar
    @staticmethod
    def create_action(parent, text, tip, connection):
        assert isinstance(parent, QMainWindow)
        assert isinstance(text, str)
        assert isinstance(tip, str)
        action = QAction(text, parent)
        action.setStatusTip(tip)
        action.setToolTip(tip)
        action.triggered.connect(connection)
        return action

    # helper-methods: load
    def load_file(self, filename):
        assert isinstance(filename, str)
        graph = Graph()
        graph.load(filename)
        self.add_graph(graph, filename)

    def add_graph(self, graph, filename):
        assert isinstance(graph, Graph)
        assert isinstance(filename, str)

        # add graph
        self._graphs.append(graph)

        # update tree
        self.browser.add_graph(graph, filename)
        self.viewer.add_graph(graph)

    # def remove_graph(self, graph):
