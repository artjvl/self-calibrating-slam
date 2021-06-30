import enum
import typing as tp

from PyQt5 import QtGui, QtWidgets
from framework.math.matrix.Matrix import SubMatrix
from src.framework.graph.BlockMatrix import SubBlockMatrix
from src.framework.graph.Graph import SubGraph, Graph, SubEdge, SubNode, SubElement, Node
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import InformationNode
from src.framework.graph.types.scslam2d.nodes.parameter.ParameterNode import ParameterNode
from src.framework.math.Dimensional import Dimensional
from src.framework.math.lie.Lie import Lie
from src.framework.math.lie.rotation.SO import SO
from src.framework.math.lie.transformation import SE2
from src.framework.math.lie.transformation.SE import SE

Item = tp.Union[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem]


class Indicator(enum.Enum):
    HESSIAN: int = 0
    MARGINAL: int = 1


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
        self._construct_graph_tree(graph, self.invisibleRootItem())

    def _construct_graph_tree(
            self,
            graph: SubGraph,
            root: Item
    ) -> Item:
        self.obj = graph

        # sub-elements
        sub_elements = self._construct_tree_property(root, 'Elements', '', bold=True)
        element_type: tp.Type[SubElement]
        for element_type in graph.get_types():
            self._construct_tree_property(
                sub_elements, f"num '{element_type.__name__}'", str(len(graph.get_of_type(element_type)))
            )
        sub_elements.setExpanded(True)

        # error
        sub_error = self._construct_tree_property(root, 'Error', '', bold=True)
        self._construct_tree_property(sub_error, 'is_perturbed', str(graph.is_perturbed()))
        self._construct_tree_property(sub_error, 'error', str(graph.compute_error()))
        sub_error.setExpanded(True)

        # metrics
        if graph.is_metric():
            sub_metrics = self._construct_tree_property(root, 'Metrics', '', bold=True)
            true: SubGraph = graph.get_true()
            sub_true = self._construct_tree_property(sub_metrics, 'true', true.to_unique())
            self._construct_graph_tree(true, sub_true)
            self._construct_tree_property(sub_metrics, 'ate', str(graph.compute_ate()))
            self._construct_tree_property(sub_metrics, 'rpe_translation', str(graph.compute_rpe_translation()))
            self._construct_tree_property(sub_metrics, 'rpe_rotation', str(graph.compute_rpe_rotation()))
            sub_metrics.setExpanded(True)

        # jacobian/hessian
        sub_linearisation = self._construct_tree_property(root, 'Linearisation', '', bold=True)
        sub_hessian = self._construct_tree_property(sub_linearisation, 'Hessian', '(...)')
        sub_hessian.obj = Indicator.HESSIAN
        sub_marginal = self._construct_tree_property(sub_linearisation, 'Marginal', '(...)')
        sub_marginal.obj = Indicator.MARGINAL
        sub_linearisation.setExpanded(True)

        # properties
        sub_properties = self._construct_tree_property(root, 'Properties', '', bold=True)
        self._construct_tree_property(sub_properties, 'path', str(graph.get_path()))
        sub_properties.setExpanded(True)
        return root

    def _construct_hessian(self, item: QtWidgets.QTreeWidgetItem, graph: SubGraph) -> None:
        nodes: tp.List[SubNode] = graph.get_nodes()
        hessian: SubBlockMatrix = graph.get_hessian()
        item.setText(1, str(hessian.shape()))
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if j <= i and not hessian[i, j].is_zero():
                    self._construct_tree_property_from_value(
                        item,
                        f'({node_i.get_id()}, {node_j.get_id()})',
                        hessian[i, j]
                    )

    def _construct_marginal(self, item: QtWidgets.QTreeWidgetItem, graph: SubGraph) -> None:
        nodes: tp.List[SubNode] = graph.get_nodes()
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

    # node
    def display_node(
            self,
            node: SubNode
    ) -> None:
        self.clear()
        self._construct_node_tree(node, self.invisibleRootItem())

    def _construct_node_tree(
            self,
            node: SubNode,
            root: Item
    ) -> Item:
        self.obj = node

        # top
        self._construct_tree_property(root, 'id', str(node.get_id()))
        self._construct_tree_property(root, 'is_fixed', str(node.is_fixed()))
        if isinstance(node, Node):
            if isinstance(node, ParameterNode):
                self._construct_tree_property(root, 'interpretation', node.get_interpretation())
            elif isinstance(node, InformationNode):
                self._construct_tree_property_from_value(root, 'matrix', node.get_info_matrix())

        # metrics
        if node.has_true():
            sub_metrics = self._construct_tree_property(root, 'Metrics', '', bold=True)
            true: SubNode = node.get_true()
            sub_true = self._construct_tree_property(sub_metrics, 'true', true.to_unique())
            self._construct_node_tree(true, sub_true)
            ate2: tp.Optional[float] = node.compute_ate2()
            if ate2 is not None:
                self._construct_tree_property(sub_metrics, 'ate2', str(ate2))
            sub_metrics.setExpanded(True)

        # value
        sub_value = self._construct_tree_property(root, 'Value', '', bold=True)
        self._construct_value_tree(sub_value, node.get_value())
        return root

    # edge
    def display_edge(
            self,
            edge: SubEdge
    ) -> None:
        self.clear()
        self._construct_edge_tree(edge, self.invisibleRootItem())

    def _construct_edge_tree(
            self,
            edge: SubEdge,
            root: Item
    ):
        self.obj = edge

        # top
        self._construct_tree_property(root, 'cardinality', str(edge.get_cardinality()))
        self._construct_tree_property_from_value(root, 'information', edge.get_info_matrix())

        # nodes
        nodes = edge.get_nodes()
        sub_nodes = self._construct_tree_property(root, 'Nodes', str(len(nodes)), bold=True)
        for node in nodes:
            sub_node = self._construct_tree_property(sub_nodes, str(node.get_id()), node.to_unique())
            self._construct_node_tree(node, sub_node)
        sub_nodes.setExpanded(True)

        # error
        sub_error = self._construct_tree_property(root, 'Error', '', bold=True)
        self._construct_tree_property_from_value(sub_error, 'error_vector', edge.error_vector())
        self._construct_tree_property(sub_error, 'error', '{:f}'.format(edge.compute_error()))
        sub_error.setExpanded(True)

        # metrics
        if edge.has_true():
            sub_metrics = self._construct_tree_property(root, 'Metrics', '', bold=True)
            true: SubEdge = edge.get_true()
            sub_true = self._construct_tree_property(sub_metrics, 'true', str(true.to_unique()))
            self._construct_edge_tree(true, sub_true)
            self._construct_tree_property_from_value(sub_metrics, 'rpe_translation2', edge.compute_rpe_translation2())
            self._construct_tree_property_from_value(sub_metrics, 'rpe_rotation', edge.compute_rpe_rotation())
            sub_metrics.setExpanded(True)

        # measurement
        sub_measurement = self._construct_tree_property(root, 'Measurement', '', bold=True)
        self._construct_value_tree(sub_measurement, edge.get_measurement())

        # estimate
        sub_estimate = self._construct_tree_property(root, 'Estimate', '', bold=True)
        self._construct_value_tree(sub_estimate, edge.get_estimate())

        # jacobian/hessian
        sub_linearisation = self._construct_tree_property(root, 'Linearisation', '', bold=True)
        jacobian: SubBlockMatrix = edge.get_jacobian()
        sub_jacobian = self._construct_tree_property(sub_linearisation, 'Jacobian', str(jacobian.shape()))
        for i, node in enumerate(nodes):
            self._construct_tree_property_from_value(sub_jacobian, str(node.get_id()), jacobian[0, i])
        sub_jacobian.setExpanded(True)

        hessian: SubBlockMatrix = edge.get_hessian()
        sub_hessian = self._construct_tree_property(sub_linearisation, 'Hessian', str(hessian.shape()))
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if j <= i:
                    self._construct_tree_property_from_value(
                        sub_hessian,
                        f'({node_i.get_id()}, {node_j.get_id()})',
                        hessian[i, j]
                    )
        sub_hessian.setExpanded(True)

        sub_linearisation.setExpanded(True)

        # root.expandAll()

    # helper-methods
    @classmethod
    def _construct_value_tree(
            cls,
            root: Item,
            value: Supported,
            expanded: bool = True
    ) -> Item:
        cls._construct_tree_property(root, 'type', type(value).__name__)
        cls._construct_tree_property_from_value(root, 'value', value)
        if isinstance(value, Dimensional):
            cls._construct_tree_property(root, 'dimension', str(value.get_dim()))
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
            bold: bool = False
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
        return item

    @classmethod
    def _construct_tree_property_from_value(
            cls,
            root: tp.Optional[Item],
            first: str,
            value: tp.Any,
            bold: bool = False
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
            bold=bold
        )
