from PyQt5.QtCore import *  # Qt.CustomContextMenu
from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout

from src.framework.graph import *
from src.viewer.Inspector import Inspector


class Browser(QTreeWidget):

    # constructor
    def __init__(self, window: QMainWindow, inspector: Inspector, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headerItem().setText(0, 'Object')
        self.headerItem().setText(1, 'Type')
        self.setColumnWidth(0, 128)
        self.setAlternatingRowColors(True)
        self.itemSelectionChanged.connect(self.handle_selection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.handle_context_menu)
        self._main = window
        self._inspector = inspector
        self._graphs = dict()

    # public methods
    def add_graph(self, graph: Graph):
        item = self.construct_graph_tree(graph)
        self.addTopLevelItem(item)
        self._graphs[graph.get_id()] = item

    def replace_graph(self, old: Graph, graph: Graph):
        old_item = self._graphs[old.get_id()]
        new_item = self.construct_graph_tree(graph)
        self._graphs[old.get_id()] = new_item
        index = self.indexOfTopLevelItem(old_item)
        self.takeTopLevelItem(index)
        self.insertTopLevelItem(index, new_item)

    def remove_graph(self, graph: Graph):
        item = self._graphs[graph.get_id()]
        self._graphs.pop(graph.get_id())
        index = self.indexOfTopLevelItem(item)
        self.takeTopLevelItem(index)

    # handlers
    def handle_selection(self):
        self._inspector.clear()
        item = self.currentItem()
        if hasattr(item, 'instance_item'):
            element = item.instance_item
            if isinstance(element, Graph):
                self._inspector.construct_graph_tree(self._inspector, element)
            elif isinstance(element, FactorNode):
                self._inspector.construct_node_tree(self._inspector, element)
            elif isinstance(element, FactorEdge):
                self._inspector.construct_edge_tree(self._inspector, element)

    def handle_context_menu(self, point):
        index = self.indexAt(point)
        if index.isValid():
            item = self.itemAt(point)
            if hasattr(item, 'instance_item'):
                element = item.instance_item
                if isinstance(element, Graph):
                    menu = QMenu()
                    action_replace = QAction('&Replace', self)
                    menu.addAction(action_replace)
                    action_delete = QAction('&Delete', self)
                    menu.addAction(action_delete)
                    action_save = QAction('&Save as', self)
                    menu.addAction(action_save)
                    action = menu.exec_(self.mapToGlobal(point))
                    if action == action_replace:
                        self._main.replace_graph(element)
                    elif action == action_delete:
                        self._main.remove_graph(element)
                    elif action == action_save:
                        print('save')
                if isinstance(element, FactorNode):
                    menu = QMenu()
                    action_focus = QAction('&Focus', self)
                    menu.addAction(action_focus)
                    action = menu.exec_(self.mapToGlobal(point))
                    if action == action_focus:
                        self._main.viewer.focus(element)

    # helper-methods:
    @classmethod
    def construct_graph_tree(cls, graph: Graph):
        browser_graph = cls.construct_tree_item(graph.get_name(short=True), 'Graph')
        browser_graph.instance_item = graph
        browser_graph.setToolTip(0, graph.get_name())
        # nodes:
        nodes = graph.get_nodes()
        browser_nodes = cls.construct_tree_item('nodes', '({})'.format(len(nodes)), root=browser_graph)
        for node in graph.get_nodes():
            browser_node = cls.construct_tree_item('id: {}'.format(node.id()), type(node).__name__, root=browser_nodes)
            browser_node.instance_item = node
        # edges:
        edges = graph.get_edges()
        browser_edges = cls.construct_tree_item('edges', '({})'.format(len(edges)), root=browser_graph)
        for edge in edges:
            browser_edge = cls.construct_tree_item('({})'.format(', '.join([str(node.id()) for node in edge.get_nodes()])), type(edge).__name__, root=browser_edges)
            browser_edge.instance_item = edge
        return browser_graph

    @classmethod
    def construct_tree_item(cls, object_string, type_string, root=None):
        item = QTreeWidgetItem(root)
        item.setText(0, object_string)
        item.setText(1, type_string)
        return item
