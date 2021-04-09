import typing as tp

from PyQt5 import QtCore, QtWidgets

from src.framework.graph.FactorGraph import SubElement, FactorNode, FactorEdge
from src.framework.graph.Graph import Graph
from src.framework.graph.protocols.Visualisable import SubVisualisable
from src.framework.graph.protocols.visualisable.DrawPoint import DrawPoint
from src.gui.info_pane.InspectorTree import InspectorTree
from src.gui.modules.Container import ViewerContainer, GraphContainer, ElementContainer, SubContainer
from src.gui.viewer.Viewer import Viewer


class BrowserTree(QtWidgets.QTreeWidget):

    # constructor
    def __init__(
            self,
            container: ViewerContainer,
            inspector: InspectorTree,
            viewer: Viewer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.headerItem().setText(0, 'Object')
        self.headerItem().setText(1, 'Type')
        self.setColumnWidth(0, 140)
        self.setAlternatingRowColors(True)
        self.itemSelectionChanged.connect(self._handle_selection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._handle_context_menu)
        self.itemChanged.connect(self._handle_checked)
        # container
        self._container: ViewerContainer = container
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
        container: GraphContainer
        for container in self._container.get_children():
            item = self._construct_graph_tree(container)
            self.addTopLevelItem(item)

    def _construct_graph_tree(self, container: GraphContainer) -> QtWidgets.QTreeWidgetItem:

        # top-level: Graph
        graph: Graph = container.get_graph()
        graph_item: QtWidgets.QTreeWidgetItem = self._construct_tree_item(
            str(graph.get_id()),
            graph.to_name()
        )
        graph_item.setToolTip(0, str(graph.get_id()))
        graph_item.setCheckState(0, QtCore.Qt.Checked if container.is_checked() else QtCore.Qt.Unchecked)
        graph_item.obj = container

        # for each Element-type in Graph
        element_type: tp.Type[SubElement]
        for element_type in graph.get_types():

            # level-2: Element-type
            elements: tp.List[SubElement] = graph.get_of_type(element_type)
            element_type_item = self._construct_tree_item(
                element_type.__name__,
                f'({len(elements)})',
                graph_item
            )

            if container.has_child(element_type):
                element_container: ElementContainer = container.get_child(element_type)
                element_type_item.setCheckState(0, QtCore.Qt.Checked if element_container.is_checked() else QtCore.Qt.Unchecked)
                element_type_item.obj = element_container

            # for each Element of Element-type
            element: SubElement
            for element in elements:

                # level-3: Element
                element_item = self._construct_tree_item(
                    f'({element.to_id()})',
                    element_type.__name__,
                    element_type_item
                )
                element_item.obj = element

        return graph_item

    def _update_browser(self):
        for i in range(self.topLevelItemCount()):
            graph_item: QtWidgets.QTreeWidgetItem = self.topLevelItem(i)
            graph_container: GraphContainer = graph_item.obj
            graph_item.setCheckState(0, QtCore.Qt.Checked if graph_container.is_checked() else QtCore.Qt.Unchecked)
            for j in range(graph_item.childCount()):
                element_item: QtWidgets.QTreeWidgetItem = graph_item.child(j)
                element_container: ElementContainer = element_item.obj
                element_item.setCheckState(0, QtCore.Qt.Checked if element_container.is_checked() else QtCore.Qt.Unchecked)

    # handlers
    def _handle_selection(self):
        self._inspector.clear()
        item = self.currentItem()
        if hasattr(item, 'obj'):
            obj: tp.Union[SubContainer, SubVisualisable] = item.obj
            if isinstance(obj, GraphContainer):
                self._inspector.construct_graph_tree(self._inspector, obj.get_graph())
            elif isinstance(obj, FactorNode):
                self._inspector.construct_node_tree(self._inspector, obj)
            elif isinstance(obj, FactorEdge):
                self._inspector.construct_edge_tree(self._inspector, obj)

    def _handle_context_menu(self, point):
        index = self.indexAt(point)
        if index.isValid():
            item = self.itemAt(point)
            if hasattr(item, 'obj'):
                obj: tp.Union[SubContainer, SubVisualisable] = item.obj
                if isinstance(obj, GraphContainer):
                    graph: Graph = obj.get_graph()

                    menu = QtWidgets.QMenu()
                    action_replace = QtWidgets.QAction('&Replace', self)
                    menu.addAction(action_replace)
                    action_delete = QtWidgets.QAction('&Delete', self)
                    menu.addAction(action_delete)
                    action_save = QtWidgets.QAction('&Save as', self)
                    menu.addAction(action_save)
                    action = menu.exec_(self.mapToGlobal(point))
                    if action == action_replace:
                        self._container.replace_graph(graph)
                    elif action == action_delete:
                        self._container.remove_graph(graph)
                    elif action == action_save:
                        print('save')
                elif isinstance(obj, DrawPoint):
                    menu = QtWidgets.QMenu()
                    action_focus = QtWidgets.QAction('&Focus', self)
                    menu.addAction(action_focus)
                    action = menu.exec_(self.mapToGlobal(point))
                    if action == action_focus:
                        self._viewer.focus(obj.draw_point())

    def _handle_checked(self, item: QtWidgets.QTreeWidgetItem, column: int):
        checked: bool = item.checkState(column) == QtCore.Qt.Checked
        if hasattr(item, 'obj'):
            container: SubContainer = item.obj
            if isinstance(container, (GraphContainer, ElementContainer)) and container.is_checked() != checked:
                self._container.toggle(container)

    # helper-methods
    @staticmethod
    def _construct_tree_item(
            object_string: str,
            type_string: str,
            root: tp.Optional[tp.Union[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem]] = None
    ):
        item = QtWidgets.QTreeWidgetItem(root)
        item.setText(0, object_string)
        item.setText(1, type_string)
        return item
