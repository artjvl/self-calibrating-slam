import pathlib

from PyQt5.QtCore import *  # QSize
from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout
from PyQt5.QtGui import *  # QDesktopServices

import pyqtgraph.opengl as gl
import pyqtgraph as qtg

from src.framework.graph import *
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
        # left:
        self.viewer = self.init_viewer()
        self.terminal = self.init_terminal()
        # top:
        self.menubar = self.init_menubar()
        # right:
        self.load = self.init_load()
        self.browser = self.init_browser()
        self.properties = self.init_properties()
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
        self.right_layout.addWidget(self.properties)
        self.layout.addLayout(self.right_layout)

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

    def init_browser(self):
        browser = QTreeWidget(self.central_widget)
        browser.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        browser.headerItem().setText(0, 'Object')
        browser.headerItem().setText(1, 'Type')
        browser.setColumnWidth(0, 140)
        browser.itemClicked.connect(self.handle_browser_clicked)
        return browser

    def init_properties(self):
        properties = QTreeWidget(self.central_widget)
        properties.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        properties.headerItem().setText(0, 'Property')
        properties.headerItem().setText(1, 'Value')
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

    def handle_browser_clicked(self, item, column):
        element = item.instance_item
        if isinstance(element, FactorGraph.Node):
            self.construct_node_tree(element)
        elif isinstance(element, FactorGraph.Edge):
            self.construct_edge_tree(element)

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
        name = pathlib.Path(filename).name
        browser_graph = QTreeWidgetItem(self.browser)
        browser_graph.setToolTip(0, name)
        browser_graph.setText(0, name)
        browser_graph.setText(1, 'Graph')
        # nodes:
        browser_nodes = QTreeWidgetItem(browser_graph)
        nodes = graph.get_nodes()
        browser_nodes.setText(0, 'nodes')
        browser_nodes.setText(1, '({})'.format(len(nodes)))
        for node in graph.get_nodes():
            browser_node = QTreeWidgetItem(browser_nodes)
            browser_node.setText(0, 'id: {}'.format(node.id()))
            browser_node.setText(1, type(node).__name__)
            browser_node.instance_item = node
        # edges:
        browser_edges = QTreeWidgetItem(browser_graph)
        edges = graph.get_edges()
        browser_edges.setText(0, 'edges')
        browser_edges.setText(1, '({})'.format(len(edges)))
        for edge in edges:
            browser_edge = QTreeWidgetItem(browser_edges)
            browser_edge.setText(0, '({})'.format(', '.join([str(node.id()) for node in edge.get_nodes()])))
            browser_edge.setText(1, type(edge).__name__)
            browser_edge.instance_item = edge

    def construct_node_tree(self, node):
        assert isinstance(node, FactorGraph.Node)
        self.properties.clear()

        # tag:
        properties_tag = QTreeWidgetItem(self.properties)
        properties_tag.setText(0, 'tag:')
        properties_tag.setText(1, "'{}'".format(type(node).tag))
        properties_tag.setFont(1, QFont('Courier New', 10))
        # id:
        properties_id = QTreeWidgetItem(self.properties)
        properties_id.setText(0, 'id:')
        properties_id.setText(1, '{}'.format(node.id()))
        properties_id.setFont(1, QFont('Courier New', 10))
        # value:
        properties_value = QTreeWidgetItem(self.properties)
        properties_value.setText(0, 'value:')
        properties_value.setText(1, '{}'.format(node.get_value()))
        properties_value.setFont(1, QFont('Courier New', 10))

    def construct_edge_tree(self, edge):
        assert isinstance(edge, FactorGraph.Edge)
        self.properties.clear()

        # tag:
        properties_tag = QTreeWidgetItem(self.properties)
        properties_tag.setText(0, 'tag:')
        properties_tag.setText(1, "'{}'".format(type(edge).tag))
        properties_tag.setFont(1, QFont('Courier New', 10))
        # nodes:
        properties_nodes = QTreeWidgetItem(self.properties)
        properties_nodes.setText(0, 'nodes:')
        nodes = edge.get_nodes()
        properties_nodes.setText(1, '({})'.format(len(nodes)))
        for i, node in enumerate(nodes):
            properties_node = QTreeWidgetItem(properties_nodes)
            properties_node.setText(0, '{}:'.format(i))
            properties_node.setText(1, '{}'.format(node))
            properties_node.setFont(1, QFont('Courier New', 10))
            properties_node.instance_item = node
        # value:
        properties_value = QTreeWidgetItem(self.properties)
        properties_value.setText(0, 'value:')
        properties_value.setText(1, '{}'.format(edge.get_value()))
        properties_value.setFont(1, QFont('Courier New', 10))
        if edge.is_uncertain():
            # information:
            properties_information = QTreeWidgetItem(self.properties)
            properties_information.setText(0, 'information:')
            properties_information.setText(1, '{}'.format(edge.get_information()))
            properties_information.setFont(1, QFont('Courier New', 10))


