import enum
import typing as tp

from PyQt5 import QtGui, QtWidgets
from src.framework.graph.Graph import SubGraph, Graph, SubEdge, SubNode, SubElement, Node
from src.framework.graph.data.DataFactory import Quantity
from src.framework.math.Dimensional import Dimensional
from src.framework.math.lie.Lie import Lie
from src.framework.math.lie.rotation.SO import SO
from src.framework.math.lie.transformation import SE2
from src.framework.math.lie.transformation.SE import SE
from src.framework.math.matrix.BlockMatrix import SubBlockMatrix
from src.framework.math.matrix.Matrix import SubMatrix

Item = tp.Union[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem]


class Indicator(enum.Enum):
    HESSIAN: int = 0
    MARGINAL: int = 1
    TRUE: int = 2


class InspectorTree(QtWidgets.QTreeWidget):

    obj: tp.Optional[tp.Union[SubGraph, SubNode, SubEdge]]

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headerItem().setText(0, 'Property')
        self.headerItem().setText(1, 'Value')
        self.setColumnWidth(0, 180)
        self.setAlternatingRowColors(True)
        self.itemSelectionChanged.connect(self.handle_expand)

        self.obj = None

    # graph
    def display_graph(
            self,
            graph: SubGraph
    ):
        self.clear()
        self.obj = graph
        self._construct_graph_tree(graph, self.invisibleRootItem())

    def _construct_graph_tree(
            self,
            graph: SubGraph,
            root: Item
    ) -> Item:
        self._construct_tree_property(root, 'name', f'{graph.get_name()}')
        self._construct_tree_property(root, 'address', f'{hex(id(graph))}')

        # graph
        sub_graph = self._construct_tree_property(root, 'Graph', '', bold=True, is_expanded=True)
        timestep: tp.Optional[float] = graph.timestep()
        self._construct_tree_property(sub_graph, 'timestep', f'{timestep:.2f}' if timestep is not None else '-')
        if graph.has_previous():
            self._construct_tree_property(sub_graph, 'previous', f'{graph.get_previous().to_unique()}')
        # self._construct_tree_property(sub_properties, 'path', str(graph.get_path()))

        # sub-elements
        sub_elements = self._construct_tree_property(root, 'Elements', '', bold=True, is_expanded=True)
        element_type: tp.Type[SubElement]
        for element_type in graph.get_types():
            self._construct_tree_property(
                sub_elements, f"num '{element_type.__name__}'", f'{len(graph.get_of_type(element_type))}'
            )

        # error
        sub_error = self._construct_tree_property(root, 'Error', '', bold=True, is_expanded=True)
        self._construct_tree_property(sub_error, 'is_consistent', f'{graph.is_consistent()}')
        self._construct_tree_property(sub_error, 'error', f'{graph.cost()}')

        # metrics
        if graph.has_truth():
            sub_metrics = self._construct_tree_property(root, 'Metrics', '', bold=True, is_expanded=True)
            truth: SubGraph = graph.get_truth()
            sub_truth = self._construct_tree_property(sub_metrics, 'truth', f'{truth.to_unique()}')
            sub_truth.obj = Indicator.TRUE
            self._construct_tree_property(sub_metrics, 'ate', f'{graph.ate()}')
            self._construct_tree_property(sub_metrics, 'rpe_translation', f'{graph.rpe_translation()}')
            self._construct_tree_property(sub_metrics, 'rpe_rotation', f'{graph.rpe_rotation()}')

        # jacobian/hessian
        sub_linearisation = self._construct_tree_property(root, 'Linearisation', '', bold=True, is_expanded=True)
        sub_hessian = self._construct_tree_property(sub_linearisation, 'Hessian', '(...)')
        sub_hessian.obj = Indicator.HESSIAN
        sub_marginal = self._construct_tree_property(sub_linearisation, 'Marginal', '(...)')
        sub_marginal.obj = Indicator.MARGINAL

        return root

    def _construct_hessian(self, item: QtWidgets.QTreeWidgetItem, graph: SubGraph) -> None:
        active_nodes: tp.List[SubNode] = graph.get_active_nodes()
        hessian: SubBlockMatrix = graph.get_hessian()
        item.setText(1, str(hessian.shape()))
        for i, node_i in enumerate(active_nodes):
            for j, node_j in enumerate(active_nodes):
                if j <= i and not hessian[i, j].is_zero():
                    self._construct_tree_property_from_value(
                        item,
                        f'({node_i.get_id()}, {node_j.get_id()})',
                        hessian[i, j]
                    )

    def _construct_marginal(self, item: QtWidgets.QTreeWidgetItem, graph: SubGraph) -> None:
        nodes: tp.List[SubNode] = graph.get_active_nodes()
        marginals: tp.List[SubMatrix] = graph.get_marginals()
        item.setText(1, f'({len(marginals)})')
        for i, node in enumerate(nodes):
            id_: int = node.get_id()
            self._construct_tree_property_from_value(
                item,
                f'({id_}, {id_})',
                marginals[i]
            )

    # handlers
    def handle_expand(self):
        item = self.currentItem()
        if hasattr(item, 'obj'):
            obj: Indicator = item.obj
            if isinstance(self.obj, Graph):
                if obj == Indicator.HESSIAN:
                    self._construct_hessian(item, self.obj)
                    delattr(item, 'obj')
                elif obj == Indicator.MARGINAL:
                    self._construct_marginal(item, self.obj)
                    delattr(item, 'obj')
                elif obj == Indicator.TRUE:
                    self.display_graph(self.obj.get_truth())

    # node
    def display_node(
            self,
            node: SubNode
    ) -> None:
        self.clear()
        self.obj = node
        self._construct_node_tree(node, self.invisibleRootItem())

    def _construct_node_tree(
            self,
            node: SubNode,
            root: Item
    ) -> Item:
        self._construct_tree_property(root, 'name', f'{node.get_name()}')
        self._construct_tree_property(root, 'address', f'{hex(id(node))}')

        # top
        sub_node = self._construct_tree_property(root, 'Node', '', bold=True, is_expanded=True)
        self._construct_tree_property(sub_node, 'id', f'{node.get_id()}')
        timestep: tp.Optional[float] = node.get_timestep()
        self._construct_tree_property(sub_node, 'timestep', f'{timestep:.2f}' if timestep is not None else '-')
        self._construct_tree_property(sub_node, 'is_fixed', f'{node.is_fixed()}')

        # metrics
        if node.has_truth():
            sub_metrics = self._construct_tree_property(root, 'Metrics', '', bold=True, is_expanded=True)
            truth: SubNode = node.get_truth()
            sub_truth = self._construct_tree_property(sub_metrics, 'truth', f'{truth.to_unique()}')
            self._construct_node_tree(truth, sub_truth)
            ate2: tp.Optional[float] = node._compute_ate2()
            if ate2 is not None:
                self._construct_tree_property(sub_metrics, 'ate2', f'{ate2}')

        # value
        sub_value = self._construct_tree_property(root, 'Value', '', bold=True, is_expanded=True)
        self._construct_value_tree(sub_value, node.get_value())
        return root

    # edge
    def display_edge(
            self,
            edge: SubEdge
    ) -> None:
        self.clear()
        self.obj = edge
        self._construct_edge_tree(edge, self.invisibleRootItem())

    def _construct_edge_tree(
            self,
            edge: SubEdge,
            root: Item
    ):
        self._construct_tree_property(root, 'name', f'{edge.get_name()}')
        self._construct_tree_property(root, 'address', f'{hex(id(edge))}')

        # top
        sub_edge = self._construct_tree_property(root, 'Edge', '', bold=True, is_expanded=True)
        timestep: tp.Optional[float] = edge.get_timestep()
        self._construct_tree_property(sub_edge, 'timestep', f'{timestep:.2f}' if timestep is not None else '-')
        self._construct_tree_property(sub_edge, 'cardinality', f'{edge.get_cardinality()}')
        self._construct_tree_property_from_value(sub_edge, 'information', edge.get_info_matrix())

        # nodes
        nodes = edge.get_nodes()
        sub_nodes = self._construct_tree_property(root, 'Nodes', f'{len(nodes)}', bold=True, is_expanded=True)
        for node in nodes:
            sub_node = self._construct_tree_property(sub_nodes, f'{node.get_id()}', node.to_unique())
            self._construct_node_tree(node, sub_node)

        # error
        sub_error = self._construct_tree_property(root, 'Error', '', bold=True, is_expanded=True)
        self._construct_tree_property_from_value(sub_error, 'error_vector', edge.error_vector())
        self._construct_tree_property(sub_error, 'cost', f'{edge.cost():f}')

        # metrics
        if edge.has_truth():
            sub_metrics = self._construct_tree_property(root, 'Metrics', '', bold=True, is_expanded=True)
            truth: SubEdge = edge.get_truth()
            sub_truth = self._construct_tree_property(sub_metrics, 'truth', f'{truth.to_unique()}')
            self._construct_edge_tree(truth, sub_truth)
            self._construct_tree_property_from_value(sub_metrics, 'rpe_translation2', edge.rpe_translation2())
            self._construct_tree_property_from_value(sub_metrics, 'rpe_rotation', edge.rpe_rotation2())

        # measurement
        sub_measurement = self._construct_tree_property(root, 'Measurement', '', bold=True)
        self._construct_value_tree(sub_measurement, edge.get_value())

        # estimate
        sub_estimate = self._construct_tree_property(root, 'Estimate', '', bold=True)
        self._construct_value_tree(sub_estimate, edge.get_estimate())

        # jacobian/hessian
        sub_linearisation = self._construct_tree_property(root, 'Linearisation', '', bold=True, is_expanded=True)
        jacobian: SubBlockMatrix = edge.get_jacobian()
        sub_jacobian = self._construct_tree_property(sub_linearisation, 'Jacobian', f'{jacobian.shape()}')
        active_nodes = edge.get_active_nodes()
        for i, node in enumerate(active_nodes):
            self._construct_tree_property_from_value(sub_jacobian, f'{node.get_id()}', jacobian[0, i])

        hessian: SubBlockMatrix = edge.get_hessian()
        sub_hessian = self._construct_tree_property(sub_linearisation, 'Hessian', f'{hessian.shape()}', is_expanded=True)
        for i, node_i in enumerate(active_nodes):
            for j, node_j in enumerate(active_nodes):
                if j <= i:
                    self._construct_tree_property_from_value(
                        sub_hessian,
                        f'({node_i.get_id()}, {node_j.get_id()})',
                        hessian[i, j]
                    )

    # helper-methods
    @classmethod
    def _construct_value_tree(
            cls,
            root: Item,
            value: Quantity,
            expanded: bool = True
    ) -> Item:
        cls._construct_tree_property(root, 'type', type(value).__name__)
        cls._construct_tree_property_from_value(root, 'value', value)
        if isinstance(value, Dimensional):
            cls._construct_tree_property(root, 'dimension', str(value.dim()))
            if isinstance(value, Lie):
                cls._construct_tree_property(root, 'dof', str(value.get_dof()))
                cls._construct_tree_property_from_value(root, 'vector', value.vector())
                if isinstance(value, SO):
                    cls._construct_tree_property_from_value(root, 'angle', value.angle())
                    cls._construct_tree_property_from_value(root, 'jacobian', value.jacobian())
                    cls._construct_tree_property_from_value(root, 'inverse_jacobian', value.inverse_jacobian)
                elif isinstance(value, SE):
                    if isinstance(value, SE2):
                        cls._construct_tree_property_from_value(root, 'translation_angle',
                                                                value.translation_angle_vector())
                    sub_translation = cls._construct_tree_property(root, 'translation', '')
                    cls._construct_value_tree(sub_translation, value.translation(), expanded=False)
                    sub_rotation = cls._construct_tree_property(root, 'rotation', '')
                    cls._construct_value_tree(sub_rotation, value.rotation(), expanded=False)
        root.setExpanded(expanded)
        return root

    @staticmethod
    def _construct_tree_property(
            root: tp.Optional[Item],
            first: str,
            second: str,
            tooltip: tp.Optional[str] = None,
            bold: bool = False,
            is_expanded: bool = False
    ) -> Item:
        item = QtWidgets.QTreeWidgetItem(root)
        if bold:
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
        item.setText(0, f'{first}:')
        item.setText(1, second)
        item.setFont(1, QtGui.QFont('Courier New', 10))
        item.setToolTip(1, tooltip)
        item.setExpanded(is_expanded)
        return item

    @classmethod
    def _construct_tree_property_from_value(
            cls,
            root: tp.Optional[Item],
            first: str,
            value: tp.Any,
            bold: bool = False,
            is_expanded: bool = False
    ):
        second: str = str(value)
        tooltip: tp.Optional[str] = None
        if hasattr(value, 'to_string'):
            tooltip = value.to_string()
        return cls._construct_tree_property(
            root,
            first,
            second,
            tooltip=tooltip,
            bold=bold,
            is_expanded=is_expanded
        )
