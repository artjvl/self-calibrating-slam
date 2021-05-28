import typing as tp

from PyQt5 import QtGui, QtWidgets
from framework.math.lie.transformation import SE2

from src.framework.graph.FactorGraph import SubFactorEdge, SubFactorNode, SubElement
from src.framework.graph.Graph import SubGraph
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import InformationNode
from src.framework.graph.types.scslam2d.nodes.parameter.ParameterNode import ParameterNode
from src.framework.math.Dimensional import Dimensional
from src.framework.math.lie.Lie import Lie
from src.framework.math.lie.rotation.SO import SO
from src.framework.math.lie.transformation.SE import SE

Item = tp.Union[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem]


class InspectorTree(QtWidgets.QTreeWidget):

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headerItem().setText(0, 'Property')
        self.headerItem().setText(1, 'Value')
        self.setColumnWidth(0, 180)
        self.setAlternatingRowColors(True)

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
        # sub-elements
        sub_elements = self._construct_tree_property(root, 'Elements', '', bold=True)
        element_type: tp.Type[SubElement]
        for element_type in graph.get_types():
            self._construct_tree_property(
                sub_elements, f"num '{element_type.__name__}'", f'{len(graph.get_of_type(element_type))}'
            )
        sub_elements.setExpanded(True)

        # error
        sub_error = self._construct_tree_property(root, 'Error', '', bold=True)
        self._construct_tree_property(sub_error, 'is_perturbed', f'{graph.is_perturbed()}')
        self._construct_tree_property(sub_error, 'error', f'{graph.compute_error()}')
        sub_error.setExpanded(True)

        # metrics
        if graph.is_metric():
            sub_metrics = self._construct_tree_property(root, 'Metrics', '', bold=True)
            true: SubGraph = graph.get_true()
            sub_true = self._construct_tree_property(sub_metrics, 'true', f'{true.to_unique()}')
            self._construct_graph_tree(true, sub_true)
            self._construct_tree_property(sub_metrics, 'ate', f'{graph.compute_ate()}')
            self._construct_tree_property(sub_metrics, 'rpe_translation', f'{graph.compute_rpe_translation()}')
            self._construct_tree_property(sub_metrics, 'rpe_rotation', f'{graph.compute_rpe_rotation()}')
            sub_metrics.setExpanded(True)

        # properties
        sub_properties = self._construct_tree_property(root, 'Properties', '', bold=True)
        self._construct_tree_property(sub_properties, 'path', f'{graph.get_path()}')
        sub_properties.setExpanded(True)
        return root

    # node
    def display_node(
            self,
            node: SubFactorNode
    ) -> None:
        self.clear()
        self._construct_node_tree(node, self.invisibleRootItem())

    def _construct_node_tree(
            self,
            node: SubFactorNode,
            root: Item
    ) -> Item:
        # top
        self._construct_tree_property(root, 'id', f'{node.get_id()}')
        self._construct_tree_property(root, 'is_fixed', f'{node.is_fixed()}')
        if isinstance(node, CalibratingNode):
            if isinstance(node, ParameterNode):
                self._construct_tree_property(root, 'interpretation', f'{node.get_interpretation()}')
            elif isinstance(node, InformationNode):
                self._construct_tree_property(root, 'matrix', f'{node.get_matrix()}')

        # metrics
        if node.has_true():
            sub_metrics = self._construct_tree_property(root, 'Metrics', '', bold=True)
            true: SubFactorNode = node.get_true()
            sub_true = self._construct_tree_property(sub_metrics, 'true', f'{true.to_unique()}')
            self._construct_node_tree(true, sub_true)
            ate2: tp.Optional[float] = node.compute_ate2()
            if ate2 is not None:
                self._construct_tree_property(sub_metrics, 'ate2', f'{ate2}')
            sub_metrics.setExpanded(True)

        # value
        sub_value = self._construct_tree_property(root, 'Value', '', bold=True)
        self._construct_value_tree(sub_value, node.get_value())
        return root

    # edge
    def display_edge(
            self,
            edge: SubFactorEdge
    ) -> None:
        self.clear()
        self._construct_edge_tree(edge, self.invisibleRootItem())

    def _construct_edge_tree(
            self,
            edge: SubFactorEdge,
            root: Item
    ):
        # top
        self._construct_tree_property(root, 'cardinality', f'{edge.get_cardinality()}')
        self._construct_tree_property(root, 'information', f'{edge.get_information()}')

        # nodes
        nodes = edge.get_nodes()
        sub_nodes = self._construct_tree_property(root, 'Nodes', f'({len(nodes)})', bold=True)
        for i, node in enumerate(nodes):
            sub_node = self._construct_tree_property(sub_nodes, f'{i}', f'{node.to_unique()}')
            self._construct_node_tree(node, sub_node)
        sub_nodes.setExpanded(True)

        # error
        sub_error = self._construct_tree_property(root, 'Error', '', bold=True)
        self._construct_tree_property(sub_error, 'error_vector', f'{edge.compute_error_vector()}')
        self._construct_tree_property(sub_error, 'error', '{:f}'.format(edge.compute_error()))
        sub_error.setExpanded(True)

        # metrics
        if edge.has_true():
            sub_metrics = self._construct_tree_property(root, 'Metrics', '', bold=True)
            true: SubFactorEdge = edge.get_true()
            sub_true = self._construct_tree_property(sub_metrics, 'true', f'{true.to_unique()}')
            self._construct_edge_tree(true, sub_true)
            self._construct_tree_property(sub_metrics, 'rpe_translation2', f'{edge.compute_rpe_translation2()}')
            self._construct_tree_property(sub_metrics, 'rpe_rotation', f'{edge.compute_rpe_rotation()}')
            sub_metrics.setExpanded(True)

        # measurement
        sub_measurement = self._construct_tree_property(root, 'Measurement', '', bold=True)
        self._construct_value_tree(sub_measurement, edge.get_measurement())

        # estimate
        sub_estimate = self._construct_tree_property(root, 'Estimate', '', bold=True)
        self._construct_value_tree(sub_estimate, edge.get_estimate())

        # root.expandAll()

    # helper-methods
    @classmethod
    def _construct_value_tree(
            cls,
            root: Item,
            value: Supported,
            expanded: bool = True
    ) -> Item:
        cls._construct_tree_property(root, 'type', f'{type(value).__name__}')
        if isinstance(value, Dimensional):
            cls._construct_tree_property(root, 'dimension', f'{value.get_dimension()}')
            if isinstance(value, Lie):
                cls._construct_tree_property(root, 'dof', f'{value.get_dof()}')
                cls._construct_tree_property(root, 'vector', f'{value.vector()}')
                if isinstance(value, SO):
                    cls._construct_tree_property(root, 'angle', f'{value.angle()}')
                    cls._construct_tree_property(root, 'jacobian', f'{value.jacobian()}')
                    cls._construct_tree_property(root, 'inverse_jacobian', f'{value.inverse_jacobian()}')
                elif isinstance(value, SE):
                    if isinstance(value, SE2):
                        cls._construct_tree_property(root, 'translation_angle', f'{value.translation_angle_vector()}')
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
        item.setToolTip(1, second)
        return item
