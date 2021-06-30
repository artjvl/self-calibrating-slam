import typing as tp

from PyQt5 import QtCore, QtWidgets, QtGui
from src.framework.graph.Graph import Graph, SubGraph, Node, Edge, SubElement
from src.framework.graph.protocols.Visualisable import SubVisualisable, Visualisable
from src.framework.graph.protocols.visualisable.DrawEdge import DrawEdge
from src.framework.graph.protocols.visualisable.DrawPoint import DrawPoint
from src.gui.info_pane.InspectorTree import InspectorTree
from src.gui.modules.Container import TopContainer, GraphContainer, ElementContainer, SubContainer, TrajectoryContainer
from src.gui.modules.PopUp import PopUp
from src.gui.viewer.Viewer import Viewer


class BrowserTree(QtWidgets.QTreeWidget):

    # constructor
    def __init__(
            self,
            container: TopContainer,
            inspector: InspectorTree,
            viewer: Viewer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container: TopContainer = container
        self._inspector: InspectorTree = inspector
        self._viewer: Viewer = viewer

        # formatting
        self.headerItem().setText(0, 'Object')
        self.headerItem().setText(1, 'Type')
        self.setColumnWidth(0, 240)
        self.setAlternatingRowColors(True)

        # selection
        self.itemSelectionChanged.connect(self._handle_selection)

        # checking
        self.itemChanged.connect(self._handle_checked)

        # context menus
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._handle_context_menu)

        # update
        self._container.signal_update.connect(self._handle_signal)

    def _construct_browser(self):
        self.clear()

        trajectory_container: TrajectoryContainer
        for trajectory_container in self._container.get_children():

            # trajectory-container
            graph_containers: tp.List[GraphContainer] = trajectory_container.get_children()
            trajectory_item: QtWidgets.QTreeWidgetItem = self._construct_tree_item(
                trajectory_container.get_name(),
                f'({len(graph_containers)})',
                None
            )
            trajectory_item.setCheckState(
                0, QtCore.Qt.Checked if trajectory_container.is_checked() else QtCore.Qt.Unchecked
            )
            trajectory_item.obj = trajectory_container
            self.addTopLevelItem(trajectory_item)
            trajectory_item.setExpanded(True)

            graph_container: GraphContainer
            for graph_container in graph_containers:

                # graph-container
                graph: SubGraph = graph_container.get_graph()
                is_true: bool = trajectory_container.has_true() and graph == trajectory_container.get_true()
                name: str = graph_container.get_name()
                if is_true:
                    name = f'[true] {name}'

                element_types: tp.List[tp.Type[SubElement]] = graph.get_types()
                graph_item: QtWidgets.QTreeWidgetItem = self._construct_tree_item(
                    name,
                    f'({len(element_types)})',
                    trajectory_item
                )

                if is_true:
                    graph_item.setForeground(0, QtGui.QBrush(QtGui.QColor("#00a000")))
                else:
                    graph_item.setForeground(0, QtGui.QBrush(QtGui.QColor("#ff0000")))

                # graph-container: checkbox
                graph_item.setCheckState(
                    0, QtCore.Qt.Checked if graph_container.is_checked() else QtCore.Qt.Unchecked
                )
                graph_item.obj = graph_container

                element_type: tp.Type[SubElement]
                for element_type in element_types:

                    # elements-container
                    elements: tp.List[SubElement] = graph.get_of_type(element_type)
                    elements_item: QtWidgets.QTreeWidgetItem = self._construct_tree_item(
                        f'{element_type.__name__}',
                        f'({len(elements)})',
                        graph_item
                    )

                    # elements-container: checkbox
                    if graph_container.has_child_type(element_type):
                        elements_container: ElementContainer = graph_container.get_child_type(element_type)
                        elements_item.setCheckState(
                            0, QtCore.Qt.Checked if elements_container.is_checked() else QtCore.Qt.Unchecked
                        )
                        elements_item.obj = elements_container

                    for element in elements:

                        # element
                        element_item = self._construct_tree_item(
                            f'({element.to_id()})',
                            f'{type(element).__name__}',
                            elements_item
                        )
                        element_item.obj = element

    def _update_browser(self):
        for i in range(self.topLevelItemCount()):
            graph_item: QtWidgets.QTreeWidgetItem = self.topLevelItem(i)
            if hasattr(graph_item, 'obj'):
                graph_container: GraphContainer = graph_item.obj
                graph_item.setCheckState(
                    0, QtCore.Qt.Checked if graph_container.is_checked() else QtCore.Qt.Unchecked
                )
                for j in range(graph_item.childCount()):
                    element_item: QtWidgets.QTreeWidgetItem = graph_item.child(j)
                    if hasattr(element_item, 'obj'):
                        element_container: ElementContainer = element_item.obj
                        element_item.setCheckState(
                            0, QtCore.Qt.Checked if element_container.is_checked() else QtCore.Qt.Unchecked
                        )

    # handlers
    def _handle_signal(self, signal: int):
        if signal >= 0:
            self._construct_browser()
        else:
            self._update_browser()

    def _handle_selection(self):
        item = self.currentItem()
        if hasattr(item, 'obj'):
            obj: tp.Union[SubContainer, SubVisualisable] = item.obj
            if isinstance(obj, GraphContainer):
                self._inspector.display_graph(obj.get_graph())
            elif isinstance(obj, Node):
                self._inspector.display_node(obj)
            elif isinstance(obj, Edge):
                self._inspector.display_edge(obj)

    def _handle_context_menu(self, point):
        index = self.indexAt(point)
        if index.isValid():
            item = self.itemAt(point)
            if hasattr(item, 'obj'):
                obj: tp.Union[SubContainer, SubVisualisable] = item.obj

                # if graph
                if isinstance(obj, TrajectoryContainer):
                    trajectory_container: TrajectoryContainer = obj
                    top_container: TopContainer = trajectory_container.get_parent()

                    # create menu
                    menu = QtWidgets.QMenu()
                    action_load = QtWidgets.QAction('&Load', self)
                    menu.addAction(action_load)
                    action_load_true = QtWidgets.QAction('Load true', self)
                    menu.addAction(action_load_true)
                    action_delete = QtWidgets.QAction('&Delete', self)
                    menu.addAction(action_delete)

                    # select action
                    action: QtWidgets.QAction = menu.exec_(self.mapToGlobal(point))
                    if action == action_load:
                        PopUp.load_with_callback(trajectory_container.add_graph)
                    elif action == action_load_true:
                        PopUp.load_with_callback(trajectory_container.add_true_graph)
                    elif action == action_delete:
                        trajectory_container.remove()

                elif isinstance(obj, GraphContainer):
                    graph_container: GraphContainer = obj
                    graph: Graph = graph_container.get_graph()
                    trajectory_container: TrajectoryContainer = graph_container.get_parent()
                    is_not_true: bool = not trajectory_container.has_true() and not graph.is_perturbed() and not graph.has_true()

                    # create menu
                    menu = QtWidgets.QMenu()
                    action_delete = QtWidgets.QAction('&Delete', self)
                    menu.addAction(action_delete)
                    action_save = QtWidgets.QAction('&Save as', self)
                    menu.addAction(action_save)
                    action_true = QtWidgets.QAction('Set as true', self)
                    if is_not_true:
                        menu.addAction(action_true)

                    # select action
                    action = menu.exec_(self.mapToGlobal(point))
                    if action == action_delete:
                        trajectory_container.remove_graph(graph_container)
                    elif action == action_save:
                        print('save')
                    elif action == action_true:
                        trajectory_container.set_as_true(graph)

                # if topological node
                elif isinstance(obj, Visualisable):
                    menu = QtWidgets.QMenu()
                    action_focus = QtWidgets.QAction('&Focus', self)
                    menu.addAction(action_focus)
                    action = menu.exec_(self.mapToGlobal(point))
                    if action == action_focus:
                        if isinstance(obj, DrawPoint):
                            self._viewer.focus(obj.draw_point())
                        elif isinstance(obj, DrawEdge):
                            self._viewer.focus(obj.draw_nodeset()[0])

    def _handle_checked(self, item: QtWidgets.QTreeWidgetItem, column: int):
        checked: bool = item.checkState(column) == QtCore.Qt.Checked
        if hasattr(item, 'obj'):
            container: SubContainer = item.obj
            if isinstance(container, (TrajectoryContainer, GraphContainer, ElementContainer)) \
                    and container.is_checked() != checked:
                self._container.toggle(container)

    # helper-methods
    @staticmethod
    def _construct_tree_item(
            object_string: str,
            type_string: str,
            root: tp.Optional[tp.Union[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem]]
    ):
        item = QtWidgets.QTreeWidgetItem(root)
        item.setText(0, object_string)
        item.setText(1, type_string)
        return item
