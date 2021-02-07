import pathlib

from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout

from src.framework.graph import *
from src.viewer.Inspector import Inspector


class Browser(QTreeWidget):

    # constructor
    def __init__(self, inspector, *args, **kwargs):
        assert isinstance(inspector, Inspector)
        super().__init__(*args, **kwargs)
        self._inspector = inspector
        self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        self.headerItem().setText(0, 'Object')
        self.headerItem().setText(1, 'Type')
        self.setColumnWidth(0, 140)
        self.setAlternatingRowColors(True)
        self.itemSelectionChanged.connect(self.handle_browser_selection)

    # handlers
    def handle_browser_selection(self):
        item = self.currentItem()
        if hasattr(item, 'instance_item'):
            self._inspector.clear()
            element = item.instance_item
            if isinstance(element, FactorGraph.Node):
                self._inspector.construct_node_tree(self._inspector, element)
            elif isinstance(element, FactorGraph.Edge):
                self._inspector.construct_edge_tree(self._inspector, element)

    def handle_graph_rightclick(self, event):
        menu = QMenu()
        action_replace = self.create_action(self, '&Replace', 'Replace graph with another file', )

    # helper-methods
    @classmethod
    def construct_graph_tree(cls, root, graph, filename):
        name = pathlib.Path(filename).name
        browser_graph = QTreeWidgetItem(root)
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