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
        self._graphs = dict()
        self._id_counter = 0

        # window
        self.setGeometry(200, 200, 1200, 1000)
        # self.centre()
        self.setWindowTitle('Graph-Viewer')

        # widgets:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        # left:
        self.viewer = self.init_viewer(self, central_widget)
        self.terminal = self.init_terminal(central_widget)
        # right:
        self.load = self.init_load(central_widget)
        self.inspector = self.init_inspector(central_widget)
        self.browser = self.init_browser(self, self.inspector, central_widget)

        # window:
        self.menubar = self.init_menubar(self.viewer)
        self.statusbar = self.statusBar()

        # layout
        layout = QHBoxLayout(central_widget)
        # left-layout:
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.viewer)
        left_layout.addWidget(self.terminal)
        layout.addLayout(left_layout)
        # right-layout:
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.load)
        right_layout.addWidget(self.browser)
        right_layout.addWidget(self.inspector)
        layout.addLayout(right_layout)

        # show
        self.show()
        # self.add_line()

    # widgets
    def init_viewer(self, window: QMainWindow, widget: QWidget) -> Viewer:
        # reference: https://pyqtgraph.readthedocs.io/en/latest/
        viewer = Viewer(window, widget)
        viewer.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        return viewer

    def init_browser(self, window: QMainWindow, inspector: Inspector, widget: QWidget) -> Browser:
        browser = Browser(window, inspector, widget)
        browser.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        return browser

    def init_inspector(self, widget: QWidget) -> Inspector:
        properties = Inspector(widget)
        properties.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        return properties

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

    def init_menubar(self, viewer: Viewer) -> QMenuBar:
        menubar = self.menuBar()

        # file-menu
        menu_file = menubar.addMenu('&File')
        menu_file.setToolTipsVisible(True)

        # file: load
        action_file_load = self.create_action('&Load', 'Load a file', self.handle_load)
        action_file_load.setShortcut('Ctrl+L')
        menu_file.addAction(action_file_load)

        # file: (separator)
        menu_file.addSeparator()

        # file: exit

        action_file_exit = self.create_action('&Quit', 'Exit application', self.handle_quit)
        action_file_exit.setShortcut('Ctrl+Q')
        menu_file.addAction(action_file_exit)

        # view-menu
        menu_view = menubar.addMenu('&View')
        menu_view.setToolTipsVisible(True)

        # view: grid
        action_view_grid = self.create_action('&Grid', 'Show/hide grid', self.handle_toggle_grid)
        action_view_grid.setCheckable(True)
        action_view_grid.setChecked(viewer.is_grid())
        menu_view.addAction(action_view_grid)

        action_view_axes = self.create_action('&Axis systems', 'Show/hide robot pose axis systems', self.handle_toggle_axes)
        action_view_axes.setCheckable(True)
        action_view_axes.setChecked(viewer.is_axes())
        menu_view.addAction(action_view_axes)

        action_view_edges = self.create_action('&Edges', 'Show/hide graph edges', self.handle_toggle_edges)
        action_view_edges.setCheckable(True)
        # action_view_edges.setEnabled(False)
        action_view_edges.setChecked(viewer.is_edges())
        menu_view.addAction(action_view_edges)

        # view: (separator)
        menu_view.addSeparator()

        # view: top
        action_view_top = self.create_action('&Top', 'Move camera to top view', self.handle_top)
        menu_view.addAction(action_view_top)

        # view: isometric
        action_view_isometric = self.create_action('&Isometric', 'Move camera to isometric view', self.handle_isometric)
        menu_view.addAction(action_view_isometric)

        # view: home
        action_view_home = self.create_action('&Home', 'Move camera to the home view', self.handle_home)
        menu_view.addAction(action_view_home)

        # about-menu
        menu_about = menubar.addMenu('&About')
        menu_about.setToolTipsVisible(True)

        # about: GitHub
        url = QUrl('https://github.com/artjvl/self-calibrating-slam')
        action_about_github = self.create_action('Go to GitHub', 'Redirect to source-code on GitHub', lambda: QDesktopServices.openUrl(url))
        menu_about.addAction(action_about_github)

        return menubar

    # actions
    def handle_load(self):
        self.add_graph()

    def handle_quit(self):
        print('Exiting application...')
        qApp.quit()

    def handle_toggle_grid(self):
        self.viewer.set_grid(not self.viewer.is_grid())

    def handle_toggle_axes(self):
        self.viewer.set_axes(not self.viewer.is_axes())

    def handle_toggle_edges(self):
        self.viewer.set_edges(not self.viewer.is_edges())

    def handle_top(self):
        print(self.viewer.set_top_view())
        print('Moved camera to top view')

    def handle_isometric(self):
        print(self.viewer.set_isometric_view())
        print('Moved camera to isometric view')

    def handle_home(self):
        print(self.viewer.set_home_view())
        print('Moved camera to the home position')

    # helper-methods: window
    def centre(self):
        # move frame to centre of screen
        frame_geometry = self.frameGeometry()
        centre = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(centre)
        self.move(frame_geometry.topLeft())

    # helper-methods: menubar
    def create_action(self, text: str, tip: str, connection):
        action = QAction(text, self)
        action.setStatusTip(tip)
        action.setToolTip(tip)
        action.triggered.connect(connection)
        return action

    # helper-methods: load
    def load_graph(self):
        print("Loading file...")
        # path = Path().absolute()
        filename = QFileDialog.getOpenFileName(self, 'Select file', '', 'g2o (*.g2o)')
        if filename[0]:
            graph = Graph()
            graph.load(filename[0])
            return graph
        return None

    def add_graph(self):
        graph = self.load_graph()
        if graph is not None:
            graph.set_id(self._id_counter)
            self._id_counter += 1
            self._graphs[graph.get_id()] = graph
            self.browser.add_graph(graph)
            self.viewer.add_graph(graph)

    def replace_graph(self, old: Graph):
        graph = self.load_graph()
        if graph is not None:
            print('Replacing graph: {}\n{}with: {}'.format(old.get_name(), ' ' * 11, graph.get_name()))
            graph.set_id(old.get_id())
            self._graphs[graph.get_id()] = graph
            self.browser.replace_graph(old, graph)
            self.viewer.replace_graph(old, graph)

    def remove_graph(self, graph: Graph):
        if graph.get_id() in self._graphs:
            print('Removing graph: {}'.format(graph.get_name()))
            self._graphs.pop(graph.get_id())
            self.browser.remove_graph(graph)
            self.viewer.remove_graph(graph)
        else:
            raise Exception('This Graph does not exist!')
