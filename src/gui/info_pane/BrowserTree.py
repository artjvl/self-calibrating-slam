from typing import *

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction

from src.framework.graph.Graph import Graph
from src.framework.graph.factor.FactorEdge import FactorEdge
from src.framework.graph.factor.FactorElement import FactorElement
from src.framework.graph.factor.FactorNode import FactorNode
from src.gui.modules.GraphContainer import GraphContainer, GraphDictTreeData
from src.gui.viewer.Viewer import Viewer
from src.gui.info_pane.InspectorTree import InspectorTree


class BrowserTree(QTreeWidget):

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            inspector: InspectorTree,
            viewer: Viewer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.headerItem().setText(0, 'Object')
        self.headerItem().setText(1, 'Type')
        self.setColumnWidth(0, 128)
        self.setAlternatingRowColors(True)
        self.itemSelectionChanged.connect(self._handle_selection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._handle_context_menu)
        self.itemChanged.connect(self._handle_checked)
        self.itemSelectionChanged.connect(self._handle_selection)
        # container
        self._container: GraphContainer = container
        self._container.signal_update.connect(self._handle_signal)
        self._inspector: InspectorTree = inspector
        self._viewer: Viewer = viewer

    def _handle_signal(self, signal: int):
        if signal >= 0:
            self._construct_browser()
        else:
            self._update_browser()

    def _construct_browser(self):
        self.clear()
        for graph in self._container.get_graphs():
            item = self._construct_graph_tree(graph.get_id())
            self.addTopLevelItem(item)

    def _construct_graph_tree(self, graph_id: int) -> QTreeWidgetItem:
        graph_value: GraphDictTreeData = self._container.get_graph_value(graph_id=graph_id)
        graph = graph_value.get_object()
        graph_item: QTreeWidgetItem = self._construct_tree_item(
            graph.get_name(short=True),
            'Graph({})'.format(graph.get_id())
        )
        graph_item.setToolTip(0, graph.get_name())
        graph_item.instance_item = graph_value
        graph_item.setCheckState(0, Qt.Checked if graph_value.is_checked() else Qt.Unchecked)
        for element_value in self._container.get_element_values(graph_id=graph.get_id()):
            element_type = element_value.get_object()
            elements = graph.get_elements_of_type(element_type)
            element_item = self._construct_tree_item(
                element_type.__name__,
                '({})'.format(len(elements)),
                graph_item
            )
            element_item.instance_item = element_value
            element_item.setCheckState(0, Qt.Checked if element_value.is_checked() else Qt.Unchecked)
            for element in graph.get_elements_of_type(element_type):
                item = self._construct_tree_item(
                    '({})'.format(element.id_string()),
                    element_type.__name__,
                    element_item
                )
                item.instance_item = element
        return graph_item

    def _update_browser(self):
        for i in range(self.topLevelItemCount()):
            graph_item: QTreeWidgetItem = self.topLevelItem(i)
            graph_value: GraphDictTreeData = graph_item.instance_item
            graph_item.setCheckState(0, Qt.Checked if graph_value.is_checked() else Qt.Unchecked)
            for j in range(graph_item.childCount()):
                element_item: QTreeWidgetItem = graph_item.child(j)
                element_value: GraphDictTreeData = element_item.instance_item
                element_item.setCheckState(0, Qt.Checked if element_value.is_checked() else Qt.Unchecked)

    # handlers
    def _handle_selection(self):
        self._inspector.clear()
        item = self.currentItem()
        if hasattr(item, 'instance_item'):
            obj = item.instance_item
            if isinstance(obj, GraphDictTreeData) and isinstance(obj.get_object(), Graph):
                self._inspector.construct_graph_tree(self._inspector, obj.get_object())
            elif isinstance(obj, FactorNode):
                self._inspector.construct_node_tree(self._inspector, obj)
            elif isinstance(obj, FactorEdge):
                self._inspector.construct_edge_tree(self._inspector, obj)

    def _handle_context_menu(self, point):
        index = self.indexAt(point)
        if index.isValid():
            item = self.itemAt(point)
            if hasattr(item, 'instance_item'):
                obj = item.instance_item
                if isinstance(obj, GraphDictTreeData) and isinstance(obj.get_object(), Graph):
                    menu = QMenu()
                    action_replace = QAction('&Replace', self)
                    menu.addAction(action_replace)
                    action_delete = QAction('&Delete', self)
                    menu.addAction(action_delete)
                    action_save = QAction('&Save as', self)
                    menu.addAction(action_save)
                    action = menu.exec_(self.mapToGlobal(point))
                    if action == action_replace:
                        self._container.replace_graph(obj.get_object())
                    elif action == action_delete:
                        self._container.remove_graph(obj.get_object())
                    elif action == action_save:
                        print('save')
                if isinstance(obj, FactorNode) and obj.is_physical:
                    menu = QMenu()
                    action_focus = QAction('&Focus', self)
                    menu.addAction(action_focus)
                    action = menu.exec_(self.mapToGlobal(point))
                    if action == action_focus:
                        self._viewer.focus(obj.get_translation3())

    def _handle_checked(self, item: QTreeWidgetItem, column: int):
        checked: bool = item.checkState(column) == Qt.Checked
        if hasattr(item, 'instance_item'):
            value: GraphDictTreeData = item.instance_item

            # check is value is changed internally (i.e., by the user via the Browser)
            if value.is_checked() != checked:
                if isinstance(value.get_object(), Graph):
                    self._container.toggle(value)
                if isinstance(value.get_object(), type(FactorElement)):
                    self._container.toggle(value)

    # helper-methods
    @staticmethod
    def _construct_tree_item(
            object_string: str,
            type_string: str,
            root: Optional[Union[QTreeWidget, QTreeWidgetItem]] = None
    ):
        item = QTreeWidgetItem(root)
        item.setText(0, object_string)
        item.setText(1, type_string)
        return item
