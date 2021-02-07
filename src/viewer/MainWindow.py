import pathlib

from PyQt5.QtCore import *  # QSize
from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout
from PyQt5.QtGui import *  # QDesktopServices

import pyqtgraph.opengl as gl
import pyqtgraph as qtg

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
        self.graphs = list()

        # grid
        self.is_grid = True
        self.grid = gl.GLGridItem(color=qtg.mkColor((255, 255, 255, 40)))
        self.grid.setSize(100, 100)
        self.grid.setSpacing(1, 1)

        # window
        self.setGeometry(200, 200, 1000, 800)
        # self.centre()
        self.setWindowTitle('Graph-Viewer')

        # widgets
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        # left:
        self.viewer = self.init_viewer()
        self.terminal = self.init_terminal()
        # top:
        self.menubar = self.init_menubar()
        # right:
        self.load = self.init_load()
        self.inspector = self.init_inspector()
        self.browser = self.init_browser()
        # bottom:
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
    def init_viewer(self) -> gl.GLViewWidget:
        # reference: https://pyqtgraph.readthedocs.io/en/latest/
        viewer = Viewer(self.central_widget)
        viewer.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        return viewer

    def init_terminal(self) -> QTextEdit:
        terminal = QTextEdit(self.central_widget)
        terminal.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
        terminal.setFont(QFont('Courier New', 10))
        return terminal

    def init_load(self) -> QPushButton:
        button_load = QPushButton(self.central_widget)
        button_load.setText('Load file')
        button_load.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        button_load.clicked.connect(self.handle_load)
        return button_load

    def init_menubar(self):
        menubar = self.menuBar()

        # file-menu
        menu_file = menubar.addMenu('&File')
        menu_file.setToolTipsVisible(True)

        # file: load
        action_file_load = self.create_action(self, '&Load', 'Load a file', self.handle_load)
        action_file_load.setShortcut('Ctrl+L')
        menu_file.addAction(action_file_load)

        # file: (separator)
        menu_file.addSeparator()

        # file: exit

        action_file_exit = self.create_action(self, '&Quit', 'Exit application', self.handle_quit)
        action_file_exit.setShortcut('Ctrl+Q')
        menu_file.addAction(action_file_exit)

        # view-menu
        menu_view = menubar.addMenu('&View')
        menu_view.setToolTipsVisible(True)

        # view: grid
        action_view_grid = self.create_action(self, '&Grid', 'Show/hide grid', self.handle_grid)
        action_view_grid.setCheckable(True)
        action_view_grid.setChecked(self.is_grid)
        self.set_grid(self.is_grid)
        menu_view.addAction(action_view_grid)

        # view: (separator)
        menu_view.addSeparator()

        # view: top
        action_view_top = self.create_action(self, '&Top', 'Move camera to top view', self.handle_top)
        menu_view.addAction(action_view_top)

        # view: isometric
        action_view_isometric = self.create_action(self, '&Isometric', 'Move camera to isometric view', self.handle_isometric)
        menu_view.addAction(action_view_isometric)

        # about-menu
        menu_about = menubar.addMenu('&About')
        menu_about.setToolTipsVisible(True)

        # about: GitHub
        url = QUrl('https://github.com/artjvl/self-calibrating-slam')
        action_about_github = self.create_action(self, 'Go to GitHub', 'Redirect to source-code on GitHub', lambda: QDesktopServices.openUrl(url))
        menu_about.addAction(action_about_github)

        return menubar

    def init_browser(self):
        browser = Browser(self.inspector, self.central_widget)
        browser.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        return browser

    def init_inspector(self):
        properties = Inspector(self.central_widget)
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

    def handle_grid(self):
        self.is_grid = not self.is_grid
        self.set_grid(self.is_grid)

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

    # helper-methods: viewer
    def set_grid(self, is_grid):
        if is_grid and self.grid not in self.viewer.items:
            self.viewer.addItem(self.grid)
            print('Grid enabled')
        elif not is_grid and self.grid in self.viewer.items:
            self.viewer.removeItem(self.grid)
            print('Grid disabled')

    def draw_graph(self, graph):
        for node in graph.get_nodes():
            axis = self.viewer.construct_axis(node.get_value())
            self.viewer.addItem(axis)

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
        self.graphs.append(graph)

        # update tree
        self.browser.construct_graph_tree(self.browser, graph, filename)
        self.draw_graph(graph)

    # def remove_graph(self, graph):
