import pathlib

from PyQt5.QtCore import *  # QSize
from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout
from PyQt5.QtGui import *  # QDesktopServices

import pyqtgraph.opengl as gl
import pyqtgraph as qtg

from src.framework.structures import *
from src.framework.groups import *
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
        browser = QTreeWidget(self.central_widget)
        browser.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        browser.headerItem().setText(0, 'Object')
        browser.headerItem().setText(1, 'Type')
        browser.setColumnWidth(0, 140)
        browser.setAlternatingRowColors(True)
        browser.itemClicked.connect(self.handle_browser_clicked)
        return browser

    def init_properties(self):
        properties = QTreeWidget(self.central_widget)
        properties.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        properties.headerItem().setText(0, 'Property')
        properties.headerItem().setText(1, 'Value')
        properties.setColumnWidth(0, 140)
        properties.setAlternatingRowColors(True)
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
        if hasattr(item, 'instance_item'):
            self.properties.clear()
            element = item.instance_item
            if isinstance(element, FactorGraph.Node):
                self.construct_node_tree(self.properties, element)
            elif isinstance(element, FactorGraph.Edge):
                self.construct_edge_tree(self.properties, element)

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
        name = pathlib.Path(filename).name
        browser_graph = QTreeWidgetItem(self.browser)
        browser_graph.setText(0, name)
        browser_graph.setText(1, 'Graph')
        browser_graph.setToolTip(0, filename)
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

    # helper-methods: properties-tree
    @classmethod
    def construct_node_tree(cls, root, node):
        assert isinstance(node, FactorGraph.Node)

        # tag:
        cls.construct_tree_property(root, 'tag', "'{}'".format(type(node).tag))
        # id:
        cls.construct_tree_property(root, 'id', '{}'.format(node.id()))
        # value:
        cls.construct_value_tree(root, 'value', node.get_value())
        root.expandAll()

    @classmethod
    def construct_edge_tree(cls, root, edge):
        assert isinstance(edge, FactorGraph.Edge)

        # tag:
        cls.construct_tree_property(root, 'tag', "'{}'".format(type(edge).tag))
        # nodes:
        tree_nodes = QTreeWidgetItem(root)
        tree_nodes.setText(0, 'nodes:')
        nodes = edge.get_nodes()
        tree_nodes.setText(1, '({})'.format(len(nodes)))
        for i, node in enumerate(nodes):
            cls.construct_tree_property(tree_nodes, '{}'.format(i), '{}'.format(node))
        # value:
        cls.construct_value_tree(root, 'value', edge.get_value())
        if edge.is_uncertain():
            # information:
            cls.construct_tree_property(root, 'information', '{}'.format(edge.get_information()))
        root.expandAll()

    @classmethod
    def construct_value_tree(cls, root, value_string, value):
        assert isinstance(root, (QTreeWidget, QTreeWidgetItem))
        assert isinstance(value, (Vector, SO, SE))
        if isinstance(value, Vector):
            cls.construct_tree_property(root, value_string, '{}'.format(value))
        else:
            cls.construct_group_tree(root, value_string, value)

    @classmethod
    def construct_group_tree(cls, root, group_string, group):
        assert isinstance(root, (QTreeWidget, QTreeWidgetItem))
        assert isinstance(group_string, str)
        assert isinstance(group, (SO, SE))
        values = QTreeWidgetItem(root)
        values.setText(0, group_string)
        # vector:
        cls.construct_tree_property(values, 'vector', '{}'.format(group.vector()))
        # matrix:
        cls.construct_tree_property(values, 'matrix', '{}'.format(group.matrix()))
        counter = 2
        if isinstance(group, SO):
            cls.construct_tree_property(values, 'angle', '{}'.format(group.angle()))
            counter += 1
            if isinstance(group, SO3):
                cls.construct_tree_property(values, 'quaternion', '{}'.format(group.quaternion()))
                cls.construct_tree_property(values, 'euler', '{}'.format(group.euler()))
                counter += 2
        elif isinstance(group, SE):
            translation = group.translation()
            cls.construct_tree_property(values, 'translation', '{}'.format(translation))
            rotation = group.rotation()
            cls.construct_group_tree(values, 'rotation', rotation)
            counter += 2
        values.setText(1, '({})'.format(counter))

    @staticmethod
    def construct_tree_property(root, property_string, value_string):
        assert isinstance(root, (QTreeWidget, QTreeWidgetItem))
        assert isinstance(property_string, str)
        assert isinstance(value_string, str)
        item = QTreeWidgetItem(root)
        item.setText(0, '{}:'.format(property_string))
        item.setText(1, value_string)
        item.setFont(1, QFont('Courier New', 10))
        item.setToolTip(1, value_string)
