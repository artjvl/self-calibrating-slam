import functools
import typing as tp

from PyQt5 import QtCore, QtWidgets, QtGui
from src.framework.graph.Graph import Node, Edge, SubElement
from src.framework.graph.protocols.Visualisable import SubVisualisable, Visualisable, DrawPoint, DrawEdge
from src.gui.modules.TreeNode import GraphTreeNode, TrajectoryTreeNode, Toggle
from src.gui.utils.PopUp import PopUp

if tp.TYPE_CHECKING:
    from src.framework.analysis.Analyser import AnalyserParameterValues, AnalyserParameterDynamics, AnalyserVariance
    from src.framework.graph.CalibratingGraph import SubCalibratingGraph
    from src.framework.graph.Graph import SubGraph
    from src.gui.info_pane.InspectorTree import InspectorTree
    from src.gui.info_pane.TimestampBox import TimestampBox
    from src.gui.modules.TreeNode import SubTreeNode, SubToggle, TopTreeNode, ElementTreeNode
    from src.gui.viewer.Viewer import Viewer


class BrowserTree(QtWidgets.QTreeWidget):

    _tree: 'TopTreeNode'
    _inspector: 'InspectorTree'
    _timestamp_box: 'TimestampBox'
    _viewer: 'Viewer'

    # constructor
    def __init__(
            self,
            tree: 'TopTreeNode',
            inspector: 'InspectorTree',
            timestamp_box: 'TimestampBox',
            viewer: 'Viewer',
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
                graph: 'SubGraph' = graph_node.get_graph()
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
                        elements_node: 'ElementTreeNode' = graph_node.get_child(name)
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
                        element_container: 'ElementTreeNode' = element_item.obj
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
            obj: tp.Union['SubTreeNode', SubVisualisable] = item.obj
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
        action: QtWidgets.QAction
        commands: tp.Dict[QtWidgets.QAction, tp.Callable] = {}
        plot_commands: tp.Dict[QtWidgets.QAction, tp.Callable] = {}

        # create menu
        menu = QtWidgets.QMenu()
        # select
        menu.addAction(('&Select'))
        # load
        commands[menu.addAction('Load')] = functools.partial(PopUp.load_with_callback, node.add_graph)
        # delete
        commands[menu.addAction('Delete')] = functools.partial(node.remove)

        graphs: tp.List['SubGraph'] = node.get_selected_graphs()
        first: 'SubGraph' = graphs[0]

        # analyse
        sub_analyse = menu.addMenu('Analyse selected')
        # analyse - metrics
        sub_analyse_metrics = sub_analyse.addMenu('Metrics')
        has_metrics: bool = self._tree.analyser().ate().is_group_eligible(graphs)
        sub_analyse_metrics.setEnabled(has_metrics)
        # analyse - metrics - ATE
        action = sub_analyse_metrics.addAction('Plot ATE')
        action.setEnabled(has_metrics)
        plot_commands[action] = functools.partial(self._tree.analyser().ate().plot_group, graphs)
        # analyse - metrics - RPE (translation)
        action = sub_analyse_metrics.addAction('Plot RPE (translation)')
        action.setEnabled(has_metrics)
        plot_commands[action] = functools.partial(self._tree.analyser().rpet().plot_group, graphs)
        # analyse - metrics - RPE (rotation)
        action = sub_analyse_metrics.addAction('Plot RPE (rotation)')
        action.setEnabled(has_metrics)
        plot_commands[action] = functools.partial(self._tree.analyser().rper().plot_group, graphs)

        # analyse - plot parameter dynamics
        sub_analyse_parameter_dynamics = sub_analyse.addMenu('Plot parameter dynamics')
        parameter_names: tp.List[str] = first.get_parameter_names()
        for parameter_name in parameter_names:
            analyser: tp.Type['AnalyserParameterDynamics'] = self._tree.analyser().parameter_dynamics()
            if analyser.is_group_eligible(graphs, parameter_name):
                commands[sub_analyse_parameter_dynamics.addAction(f"'{parameter_name}'")] = functools.partial(
                    analyser.plot_group, graphs, parameter_name
                )
        sub_analyse_parameter_dynamics.setEnabled(bool(sub_analyse_parameter_dynamics.actions()))
        # analyse - plot parameter
        sub_analyse_plot_parameters = sub_analyse.addMenu('Plot parameters')
        parameter_names: tp.List[str] = first.get_parameter_names()
        for parameter_name in parameter_names:
            analyser: tp.Type['AnalyserParameterValues'] = self._tree.analyser().parameter_values()
            if analyser.is_group_eligible(graphs, parameter_name):
                plot_commands[sub_analyse_plot_parameters.addAction(f"'{parameter_name}'")] = functools.partial(
                    analyser.plot_group, graphs, parameter_name
                )
        sub_analyse_plot_parameters.setEnabled(bool(sub_analyse_plot_parameters.actions()))
        # analyse - plot estimate variance
        sub_analyse_plot_estimate_variance = sub_analyse.addMenu('Plot estimated variance')
        edge_names: tp.List[str] = first.get_edge_names()
        for edge_name in edge_names:
            analyser: tp.Type['AnalyserVariance'] = self._tree.analyser().variance()
            plot_commands[sub_analyse_plot_estimate_variance.addAction(f"'{edge_name}'")] = functools.partial(
                analyser.plot_group_estimate_variance, graphs, edge_name
            )
        sub_analyse_plot_estimate_variance.setEnabled(bool(sub_analyse_plot_estimate_variance.actions()))

        # select action
        action = menu.exec_(self.mapToGlobal(point))
        if action in commands:
            commands[action]()
        elif action in plot_commands:
            self._tree.analyser().set_fig(plot_commands[action]())

    def _open_graph_context(
            self,
            node: GraphTreeNode,
            point
    ) -> None:
        graph: 'SubCalibratingGraph' = node.get_graph()
        action: QtWidgets.QAction
        commands: tp.Dict[QtWidgets.QAction, tp.Callable] = {}
        plot_commands: tp.Dict[QtWidgets.QAction, tp.Callable] = {}

        # create menu
        menu = QtWidgets.QMenu()
        # select
        menu.addAction('&Select')
        # delete
        commands[menu.addAction('&Delete')] = functools.partial(node.remove)
        # save as
        commands[menu.addAction('&Save as')] = functools.partial(PopUp.save_file, graph)
        # find subgraphs
        action_find_subgraphs: QtWidgets.QAction = menu.addAction('Find subgraphs')
        action_find_subgraphs.setEnabled(node.is_singular())
        # set as truth
        action = menu.addAction('Set as truth')
        action.setEnabled(node.is_eligible_for_truth())
        commands[action] = functools.partial(node.set_as_truth)

        # analyse
        sub_analyse = menu.addMenu('Analyse')
        # analyse - plot graph
        action = sub_analyse.addAction('Plot graph')
        plot_commands[action] = functools.partial(self._tree.analyser().topology().plot, graph)

        # analyse - metrics
        sub_analyse_metrics = sub_analyse.addMenu('Metrics')
        has_metrics: bool = self._tree.analyser().ate().is_eligible(graph)
        sub_analyse_metrics.setEnabled(has_metrics)
        # analyse - metrics - ATE
        action = sub_analyse_metrics.addAction('Plot ATE')
        action.setEnabled(has_metrics)
        plot_commands[action] = functools.partial(self._tree.analyser().ate().plot, graph)
        # analyse - metrics - RPE (translation)
        action = sub_analyse_metrics.addAction('Plot RPE (translation')
        action.setEnabled(has_metrics)
        plot_commands[action] = functools.partial(self._tree.analyser().rpet().plot, graph)
        # analyse - metrics - RPE (rotation)
        action = sub_analyse_metrics.addAction('Plot RPE (rotation)')
        action.setEnabled(has_metrics)
        plot_commands[action] = functools.partial(self._tree.analyser().rper().plot, graph)

        # analyse - plot parameter dynamics
        sub_analyse_parameter_dynamics = sub_analyse.addMenu('Plot parameter dynamics')
        parameter_names: tp.List[str] = graph.get_parameter_names()
        for parameter_name in parameter_names:
            analyser: tp.Type['AnalyserParameterDynamics'] = self._tree.analyser().parameter_dynamics()
            if analyser.is_eligible(graph, parameter_name):
                plot_commands[sub_analyse_parameter_dynamics.addAction(f"'{parameter_name}'")] = functools.partial(
                    self._tree.analyser().parameter_dynamics().plot, graph, parameter_name
                )
        sub_analyse_parameter_dynamics.setEnabled(bool(sub_analyse_parameter_dynamics.actions()))
        # analyse - plot parameter
        sub_analyse_plot_parameters = sub_analyse.addMenu('Plot parameter values')
        parameter_names: tp.List[str] = graph.get_parameter_names()
        for parameter_name in parameter_names:
            analyser: tp.Type['AnalyserParameterValues'] = self._tree.analyser().parameter_values()
            if analyser.is_eligible(graph, parameter_name):
                plot_commands[sub_analyse_plot_parameters.addAction(f"'{parameter_name}'")] = functools.partial(
                    analyser.plot, graph, parameter_name
                )
        sub_analyse_plot_parameters.setEnabled(bool(sub_analyse_plot_parameters.actions()))
        # analyse - plot edge variance
        sub_analyse_plot_edge_variance = sub_analyse.addMenu('Plot edge variance')
        edge_names: tp.List[str] = graph.get_edge_names()
        for edge_name in edge_names:
            analyser: tp.Type['AnalyserVariance'] = self._tree.analyser().variance()
            plot_commands[sub_analyse_plot_edge_variance.addAction(f"'{edge_name}'")] = functools.partial(
                analyser.plot_edge_variance, graph, edge_name
            )
        sub_analyse_plot_edge_variance.setEnabled(bool(sub_analyse_plot_edge_variance.actions()))
        # analyse - plot estimate variance
        sub_analyse_plot_estimate_variance = sub_analyse.addMenu('Plot estimated variance')
        edge_names: tp.List[str] = graph.get_edge_names()
        for edge_name in edge_names:
            analyser: tp.Type['AnalyserVariance'] = self._tree.analyser().variance()
            plot_commands[sub_analyse_plot_estimate_variance.addAction(f"'{edge_name}'")] = functools.partial(
                analyser.plot_estimate_variance, graph, edge_name
            )
        sub_analyse_plot_estimate_variance.setEnabled(bool(sub_analyse_plot_estimate_variance.actions()))

        # select action
        action = menu.exec_(self.mapToGlobal(point))
        if action in commands:
            commands[action]()
        elif action in plot_commands:
            self._tree.analyser().set_fig(plot_commands[action]())
        elif action == action_find_subgraphs:
            node.find_subgraphs()
            self._timestamp_box.update_contents()

    def _handle_context_menu(self, point):
        index = self.indexAt(point)
        if index.isValid():
            item = self.itemAt(point)
            if hasattr(item, 'obj'):
                obj: tp.Union['SubTreeNode', SubVisualisable] = item.obj

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
            toggle: 'SubToggle' = item.obj

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
