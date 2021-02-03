import numpy as np
from pathlib import Path

from PyQt5.QtCore import *  # QSize
from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout
from PyQt5.QtGui import *  # QDesktopServices
import pyqtgraph.opengl as gl

from stl import mesh


class GraphViewer(QMainWindow):

    # constructor
    def __init__(self):
        super(GraphViewer, self).__init__()

        # grid
        self.is_grid = True
        self.grid = gl.GLGridItem()
        self.grid.setSize(100, 100)
        self.grid.setSpacing(1, 1)

        # window
        self.setGeometry(200, 200, 1000, 800)
        # self.centre()
        self.setWindowTitle('Graph-Viewer')

        # widgets
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.viewer = self.init_viewer()
        self.menubar = self.init_menubar()
        self.terminal = self.init_terminal()
        self.sidebar = self.init_sidebar()

        # layout
        self.layout = QHBoxLayout(self.central_widget)
        # left-layout
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.viewer)
        self.left_layout.addWidget(self.terminal)
        self.layout.addLayout(self.left_layout)
        # right-layout
        self.layout.addLayout(self.sidebar)

        # show
        self.show()

    # widgets
    def init_viewer(self) -> gl.GLViewWidget:
        viewer = gl.GLViewWidget(self.central_widget)
        viewer.setMinimumSize(QSize(600, 400))
        viewer.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        viewer.setCameraPosition(distance=40)
        return viewer

    def init_terminal(self) -> QTextEdit:
        terminal = QTextEdit(self.central_widget)
        terminal.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
        return terminal

    def init_sidebar(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        # button
        button_load = QPushButton(self.central_widget)
        button_load.setText('Load file')
        button_load.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        button_load.clicked.connect(self.on_load)
        layout.addWidget(button_load)

        # text
        info_pane = QTextEdit(self.central_widget)
        info_pane.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        layout.addWidget(info_pane)

        return layout


    def init_menubar(self):
        menubar = self.menuBar()

        # file-menu
        menu_file = menubar.addMenu('&File')

        # file: load
        action_file_load = QAction('&Load', self)
        action_file_load.setShortcut('Ctrl+L')
        action_file_load.setStatusTip('Load file')
        action_file_load.triggered.connect(self.on_load)
        menu_file.addAction(action_file_load)

        # file: (separator)
        menu_file.addSeparator()

        # file: exit
        action_file_exit = QAction('&Quit', self)
        action_file_exit.setShortcut('Ctrl+Q')
        action_file_exit.setStatusTip('Exit application')
        action_file_exit.triggered.connect(self.on_quit)
        menu_file.addAction(action_file_exit)

        # view-menu
        menu_view = menubar.addMenu('&View')

        # view: grid
        action_view_grid = QAction('&Grid', self)
        action_view_grid.setStatusTip('Show/hide grid')
        action_view_grid.setCheckable(True)
        action_view_grid.setChecked(self.is_grid)
        self.set_grid(self.is_grid)
        action_view_grid.triggered.connect(self.on_grid)
        menu_view.addAction(action_view_grid)

        # about-menu
        menu_about = menubar.addMenu('&About')

        # about: GitHub
        link_string = 'https://github.com/artjvl/self-calibrating-slam'
        action_about_github = QAction('Go to GitHub', self)
        action_about_github.setStatusTip('Redirect to source-code on GitHub')
        action_about_github.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(link_string)))
        menu_about.addAction(action_about_github)

        return menubar

    # actions
    def on_load(self):
        print("Loading file...")
        # path = Path().absolute()
        file_name = QFileDialog.getOpenFileName(self, 'Select file', '', 'STL (*.stl)')
        if file_name[0]:
            self.load_file(file_name[0])
        self.load_file()

    def on_quit(self):
        print('Exiting application...')
        qApp.quit()

    def on_grid(self):
        self.is_grid = not self.is_grid
        self.set_grid(self.is_grid)

    # methods
    def set_grid(self, is_grid):
        if is_grid and self.grid not in self.viewer.items:
            self.viewer.addItem(self.grid)
            print('Grid enabled')
        elif not is_grid and self.grid in self.viewer.items:
            self.viewer.removeItem(self.grid)
            print('Grid disabled')

    def centre(self):
        # move frame to centre of screen
        frame_geometry = self.frameGeometry()
        centre = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(centre)
        self.move(frame_geometry.topLeft())

    def load_file(self, file='data/torus.stl'):
        self.viewer.setCameraPosition(distance=40)
        m = mesh.Mesh.from_file(file)
        points = m.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        meshdata = gl.MeshData(vertexes=points, faces=faces)
        mesh_ = gl.GLMeshItem(meshdata=meshdata, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))
        self.viewer.addItem(mesh_)
