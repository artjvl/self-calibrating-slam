import numpy as np
from pathlib import Path

from PyQt5.QtCore import *  # QSize
from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout
from PyQt5.QtGui import *  # QDesktopServices

import pyqtgraph.opengl as gl
import pyqtgraph as qtg

from stl import mesh

from src.viewer.Drawer import Drawer


class GraphViewer(QMainWindow):
    # reference: https://memotut.com/create-a-3d-model-viewer-with-pyqt5-and-pyqtgraph-b3916/
    #            https://github.com/Be4rR/STLViewer

    # constructor
    def __init__(self):
        super(GraphViewer, self).__init__()
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
        self.viewer = self.init_viewer()
        self.menubar = self.init_menubar()
        self.terminal = self.init_terminal()
        self.sidebar = self.init_sidebar()
        self.statusbar = self.statusBar()

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
        # self.add_line()

    # widgets
    def init_viewer(self) -> gl.GLViewWidget:
        # reference: https://pyqtgraph.readthedocs.io/en/latest/
        viewer = gl.GLViewWidget(self.central_widget)
        viewer.setMinimumSize(QSize(600, 400))
        viewer.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        viewer.setCameraPosition(distance=40)
        viewer.addItem(Drawer.axis())
        return viewer

    def init_terminal(self) -> QTextEdit:
        terminal = QTextEdit(self.central_widget)
        terminal.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
        terminal.setFont(QFont('Courier New', 10))
        return terminal

    def init_sidebar(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        # button
        button_load = QPushButton(self.central_widget)
        button_load.setText('Load file')
        button_load.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        button_load.clicked.connect(self.handle_load)
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
        menu_file.setToolTipsVisible(True)

        # file: load
        action_file_load = QAction('&Load', self)
        action_file_load.setShortcut('Ctrl+L')
        action_file_load_tip = 'Load a file'
        action_file_load.setStatusTip(action_file_load_tip)
        action_file_load.setToolTip(action_file_load_tip)
        action_file_load.triggered.connect(self.handle_load)
        menu_file.addAction(action_file_load)

        # file: (separator)
        menu_file.addSeparator()

        # file: exit
        action_file_exit = QAction('&Quit', self)
        action_file_exit.setShortcut('Ctrl+Q')
        action_file_exit_tip = 'Exit application'
        action_file_exit.setStatusTip(action_file_exit_tip)
        action_file_exit.setToolTip(action_file_exit_tip)
        action_file_exit.triggered.connect(self.handle_quit)
        menu_file.addAction(action_file_exit)

        # view-menu
        menu_view = menubar.addMenu('&View')
        menu_view.setToolTipsVisible(True)

        # view: grid
        action_view_grid = QAction('&Grid', self)
        action_view_grid_tip = 'Show/hide grid'
        action_view_grid.setCheckable(True)
        action_view_grid.setChecked(self.is_grid)
        action_view_grid.setStatusTip(action_view_grid_tip)
        action_view_grid.setToolTip(action_view_grid_tip)
        self.set_grid(self.is_grid)
        action_view_grid.triggered.connect(self.handle_grid)
        menu_view.addAction(action_view_grid)

        # view: (separator)
        menu_view.addSeparator()

        # view: top
        action_view_top = QAction('&Top', self)
        action_view_top_tip = 'Move camera to top view'
        action_view_top.setStatusTip(action_view_top_tip)
        action_view_top.setToolTip(action_view_top_tip)
        action_view_top.triggered.connect(self.handle_top)
        menu_view.addAction(action_view_top)

        # view: isometric
        action_view_isometric = QAction('&Isometric', self)
        action_view_isometric_tip = 'Move camera to isometric view'
        action_view_isometric.setStatusTip(action_view_isometric_tip)
        action_view_isometric.setToolTip(action_view_isometric_tip)
        action_view_isometric.triggered.connect(self.handle_isometric)
        menu_view.addAction(action_view_isometric)

        # about-menu
        menu_about = menubar.addMenu('&About')
        menu_about.setToolTipsVisible(True)

        # about: GitHub
        url = QUrl('https://github.com/artjvl/self-calibrating-slam')
        action_about_github = QAction('Go to GitHub', self)
        action_about_github_tip = 'Redirect to source-code on GitHub'
        action_about_github.setStatusTip(action_about_github_tip)
        action_about_github.setToolTip(action_about_github_tip)
        action_about_github.triggered.connect(lambda: QDesktopServices.openUrl(url))
        menu_about.addAction(action_about_github)

        return menubar

    # actions
    def handle_load(self):
        print("Loading file...")
        # path = Path().absolute()
        file_name = QFileDialog.getOpenFileName(self, 'Select file', '', 'STL (*.stl)')
        if file_name[0]:
            self.load_file(file_name[0])
        self.load_file()

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

    # methods
    def set_grid(self, is_grid):
        if is_grid and self.grid not in self.viewer.items:
            self.viewer.addItem(self.grid)
            print('Grid enabled')
        elif not is_grid and self.grid in self.viewer.items:
            self.viewer.removeItem(self.grid)
            print('Grid disabled')

    # def add_line(self):
    #     pos = np.array([[0, 0, 0],
    #                     [2, 1, 0]])
    #     line = gl.GLLinePlotItem(pos=pos, width=2)
    #     width = 0.1
    #     cyl = gl.MeshData.cylinder(1, 12, radius=[0.5*width, 0.5*width])
    #     self.viewer.addItem(gl.GLMeshItem(meshdata=cyl, drawFaces=False, drawEdges=True))
    #     self.viewer.addItem(line)

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
