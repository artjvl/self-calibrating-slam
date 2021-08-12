import typing as tp

from PyQt5 import QtCore, QtWidgets, QtGui
from src.framework.graph.Graph import SubGraph, Node, Edge, SubElement
from src.framework.graph.GraphAnalyser import GraphAnalyser
from src.framework.graph.protocols.Visualisable import SubVisualisable, Visualisable, DrawPoint, DrawEdge
from src.gui.info_pane.InspectorTree import InspectorTree
from src.gui.info_pane.TimestampBox import TimestampBox
from src.gui.modules.TreeNode import TopTreeNode, GraphTreeNode, ElementTreeNode, SubTreeNode, TrajectoryTreeNode, \
    SubToggle, Toggle
from src.gui.utils.PopUp import PopUp
from src.gui.viewer.Viewer import Viewer


class BrowserTree(QtWidgets.QTreeWidget):

    _tree: TopTreeNode
    _inspector: InspectorTree
    _timestamp_box: TimestampBox
    _viewer: Viewer

    # constructor
    def __init__(
            self,
            tree: TopTreeNode,
            inspector: InspectorTree,
            timestamp_box: TimestampBox,
            viewer: Viewer,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._tree = tree
        self._inspector = inspector
        self._timestamp_box = timestamp_box
        self._viewer = viewer

        # formatting
        self.headerItem().setText(0, 'Object')
        self.headerItem().setText(1, 'Type')
        self.setColumnWidth(0, 300)
        self.setAlternatingRowColors(True)

        # selection
        self.itemSelectionChanged.connect(self._handle_selection)

        # checking
        self.itemChanged.connect(self._handle_checked)

        # context menus
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._handle_context_menu)

        # update
        self._tree.signal_update.connect(self._handle_signal)

    def _construct_browser(self):
        self.clear()

        trajectory_node: TrajectoryTreeNode
        for trajectory_node in self._tree.get_children():

            # trajectory-container
            graph_nodes: tp.List[GraphTreeNode] = trajectory_node.get_children()
            trajectory_item: QtWidgets.QTreeWidgetItem = self._construct_tree_item(
                trajectory_node.get_gui_name(),
                f'({len(graph_nodes)})',
                None
            )
            trajectory_item.setCheckState(
                0, QtCore.Qt.Checked if trajectory_node.is_checked() else QtCore.Qt.Unchecked
            )
            trajectory_item.obj = trajectory_node
            self.addTopLevelItem(trajectory_item)
            trajectory_item.setExpanded(True)

            graph_node: GraphTreeNode
            for graph_node in graph_nodes:

                # graph-container
                graph: SubGraph = graph_node.get_graph()
                is_truth: bool = trajectory_node.has_truth() and trajectory_node.get_truth() == graph_node.get_graph_container()
                name: str = graph_node.get_gui_name()
                if is_truth:
                    name = f'[truth] {name}'

                names: tp.List[str] = graph.get_names()
                graph_item: QtWidgets.QTreeWidgetItem = self._construct_tree_item(
                    name,
                    f'({len(names)})',
                    trajectory_item
                )

                if is_truth:
                    graph_item.setForeground(0, QtGui.QBrush(QtGui.QColor("#00a000")))
                else:
                    graph_item.setForeground(0, QtGui.QBrush(QtGui.QColor("#ff0000")))

                # graph-container: checkbox
                graph_item.setCheckState(
                    0, QtCore.Qt.Checked if graph_node.is_checked() else QtCore.Qt.Unchecked
                )
                graph_item.obj = graph_node

                name: str
                for name in names:

                    # elements-container
                    elements: tp.List[SubElement] = graph.get_of_name(name)
                    elements_item: QtWidgets.QTreeWidgetItem = self._construct_tree_item(
                        f"'{name}' ({graph.get_type_of_name(name).__name__})",
                        f'({len(elements)})',
                        graph_item
                    )

                    # elements-container: checkbox
                    if graph_node.has_key(name):
                        elements_node: ElementTreeNode = graph_node.get_child(name)
                        elements_item.setCheckState(
                            0, QtCore.Qt.Checked if elements_node.is_checked() else QtCore.Qt.Unchecked
                        )
                        elements_item.obj = elements_node
                    else:
                        text: str = elements_item.text(0)
                        elements_item.setText(0, "{}  {}".format(u'\u2014', text))

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
                graph_container: GraphTreeNode = graph_item.obj
                graph_item.setCheckState(
                    0, QtCore.Qt.Checked if graph_container.is_checked() else QtCore.Qt.Unchecked
                )
                for j in range(graph_item.childCount()):
                    element_item: QtWidgets.QTreeWidgetItem = graph_item.child(j)
                    if hasattr(element_item, 'obj'):
                        element_container: ElementTreeNode = element_item.obj
                        element_item.setCheckState(
                            0, QtCore.Qt.Checked if element_container.is_checked() else QtCore.Qt.Unchecked
                        )

    # handlers
    def _handle_signal(self, signal: int):
        if signal > 0:
            # tree contents have been changed (i.e., a graph added or removed)
            self._construct_browser()
        elif signal == 0:
            self._construct_browser()
            self._inspector.clear()
            self._timestamp_box.clear()
        else:
            # element has been toggled
            self._update_browser()

    def _handle_selection(self):
        item = self.currentItem()
        if hasattr(item, 'obj'):
            obj: tp.Union[SubTreeNode, SubVisualisable] = item.obj
            if isinstance(obj, GraphTreeNode):
                self._inspector.display_graph(obj.get_graph())
                self._timestamp_box.set_node(obj)
            elif isinstance(obj, Node):
                self._inspector.display_node(obj)
            elif isinstance(obj, Edge):
                self._inspector.display_edge(obj)

    def _open_trajectory_context(
            self,
            node: TrajectoryTreeNode,
            point
    ) -> None:
        menu = QtWidgets.QMenu()
        action_load = QtWidgets.QAction('&Load', self)
        menu.addAction(action_load)
        # action_load_truth = QtWidgets.QAction('Load truth', self)
        # menu.addAction(action_load_truth)
        action_delete = QtWidgets.QAction('&Delete', self)
        menu.addAction(action_delete)

        # select action
        action: QtWidgets.QAction = menu.exec_(self.mapToGlobal(point))
        if action == action_load:
            PopUp.load_with_callback(node.add_graph)
        # elif action == action_load_truth:
        #     PopUp.load_with_callback(node.add_truth_graph)
        elif action == action_delete:
            node.remove()

    def _open_graph_context(
            self,
            node: GraphTreeNode,
            point
    ) -> None:
        graph: SubGraph = node.get_graph()

        # create menu
        menu = QtWidgets.QMenu()
        # delete
        action_delete = menu.addAction('&Delete')
        # save as
        action_save = menu.addAction('&Save as')
        # find subgraphs
        action_subgraphs = menu.addAction('Find subgraphs')
        action_subgraphs.setEnabled(node.is_singular())
        # set as truth
        action_truth = menu.addAction('Set as truth')
        action_truth.setEnabled(node.is_eligible_for_truth())
        # analyse
        sub_analyse = menu.addMenu('Analyse')
        # analyse - plot graph
        action_plot = sub_analyse.addAction('Plot graph')
        # analyse - metrics - ate
        sub_analyse_metrics = sub_analyse.addMenu('Metrics')
        action_ate = sub_analyse_metrics.addAction('Plot ATE')
        action_ate.setEnabled(not node.is_singular() and graph.is_perturbed())

        # action_slice = QtWidgets.QAction('Plot error-curve', self)
        # menu.addAction(action_slice)
        # can_be_sliced: bool = graph.has_truth() and graph.has_pre()
        # if not can_be_sliced:
        #     action_slice.setEnabled(False)
        #
        # action_metrics = QtWidgets.QAction('Plot metrics', self)
        # menu.addAction(action_metrics)
        # if not graph.has_truth():
        #     action_metrics.setEnabled(False)

        # select action
        action = menu.exec_(self.mapToGlobal(point))
        if action == action_delete:
            node.remove()
        elif action == action_save:
            print('save')
        elif action == action_subgraphs:
            node.find_subgraphs()
            self._timestamp_box.update_contents()
        elif action == action_truth:
            node.set_as_truth()
        elif action == action_plot:
            self._tree.get_analyser().plot_topology(graph)
        elif action == action_ate:
            self._tree.get_analyser().plot_ate(graph)


        # elif action == action_truth:
        #     trajectory_container.set_as_truth(graph)
        # elif action == action_slice:
        #     GraphAnalyser.plot_error_slice(graph)
        # elif action == action_metrics:
        #     GraphAnalyser.plot_metrics(graph)

    def _handle_context_menu(self, point):
        index = self.indexAt(point)
        if index.isValid():
            item = self.itemAt(point)
            if hasattr(item, 'obj'):
                obj: tp.Union[SubTreeNode, SubVisualisable] = item.obj

                # if graph
                if isinstance(obj, TrajectoryTreeNode):
                    self._open_trajectory_context(obj, point)

                elif isinstance(obj, GraphTreeNode):
                    self._open_graph_context(obj, point)

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
        """
        Handler for checking checkboxes. Checking checkboxes is done via:
        - widget interaction by user
        - setCheckState, which is called from '_construct_browser' and '_update_browser' (via handling of
          self._container.signal_update)
        """
        checked: bool = item.checkState(column) == QtCore.Qt.Checked
        if hasattr(item, 'obj') and isinstance(item.obj, Toggle):
            toggle: SubToggle = item.obj

            # check if by checked by user:
            if toggle.is_checked() != checked:
                toggle.toggle()

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
