import typing as tp

from PyQt5 import QtGui, QtWidgets

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

    # helper-methods
    def construct_graph_tree(
            self,
            graph: SubGraph
    ):
        self.clear()

        # sub-elements
        sub_elements = self._construct_tree_property(self, 'Elements', '')
        element_type: tp.Type[SubElement]
        for element_type in graph.get_types():
            self._construct_tree_property(
                sub_elements, f"num '{element_type.__name__}'", f'{len(graph.get_of_type(element_type))}'
            )

        # error
        sub_error = self._construct_tree_property(self, 'Error', '')
        self._construct_tree_property(sub_error, 'is_perturbed', f'{graph.is_perturbed()}')
        self._construct_tree_property(sub_error, 'error', f'{graph.compute_error()}')

        # metrics
        if graph.is_metric():
            sub_metrics = self._construct_tree_property(self, 'Metrics', '')
            self._construct_tree_property(sub_metrics, 'ate', f'{graph.compute_ate()}')
            self._construct_tree_property(sub_metrics, 'rpe_translation', f'{graph.compute_rpe_translation()}')
            self._construct_tree_property(sub_metrics, 'rpe_rotation', f'{graph.compute_rpe_rotation()}')

        self.expandAll()

    def construct_node_tree(
            self,
            node: SubFactorNode
    ):
        self.clear()

        self._construct_tree_property(self, 'id', f'{node.get_id()}')
        self._construct_tree_property(self, 'is_fixed', f'{node.is_fixed()}')
        if isinstance(node, CalibratingNode):
            if isinstance(node, ParameterNode):
                self._construct_tree_property(self, 'interpretation', f'{node.get_interpretation()}')
            elif isinstance(node, InformationNode):
                self._construct_tree_property(self, 'matrix', f'{node.get_matrix()}')
        sub_value: Item = self._construct_value_tree(self, 'value', node.get_value())
        sub_value.setExpanded(True)
        # root.expandAll()

    def construct_edge_tree(
            self,
            edge: SubFactorEdge
    ):
        self.clear()

        sub_nodes: Item = QtWidgets.QTreeWidgetItem(self)
        sub_nodes.setText(0, 'nodes:')
        nodes = edge.get_nodes()
        sub_nodes.setText(1, '({})'.format(len(nodes)))
        for i, node in enumerate(nodes):
            self._construct_tree_property(sub_nodes, f'{i}', f'{node.to_unique()}')
        sub_nodes.setExpanded(True)

        self._construct_tree_property(self, 'cardinality', f'{edge.get_cardinality()}')
        self._construct_tree_property(self, 'information', f'{edge.get_information()}')
        self._construct_tree_property(self, 'error_vector', f'{edge.compute_error_vector()}')
        self._construct_tree_property(self, 'error', '{:f}'.format(edge.compute_error()))

        # if isinstance(edge, CalibratingEdge):
        #

        sub_measurement: Item = self._construct_value_tree(self, 'measurement', edge.get_measurement())
        sub_measurement.setExpanded(True)
        sub_estimate: Item = self._construct_value_tree(self, 'estimate', edge.get_estimate())
        sub_estimate.setExpanded(True)
        # root.expandAll()

    @classmethod
    def _construct_value_tree(
            cls,
            root: Item,
            name: str,
            value: Supported
    ) -> Item:
        sub = QtWidgets.QTreeWidgetItem(root)
        sub.setText(0, f'{name}:')
        sub.setText(1, f'{type(value).__name__}')
        cls._construct_tree_property(sub, 'value', f'{value}')
        if isinstance(value, Dimensional):
            cls._construct_tree_property(sub, 'dimension', f'{value.get_dimension()}')
            if isinstance(value, Lie):
                cls._construct_tree_property(sub, 'dof', f'{value.get_dof()}')
                cls._construct_tree_property(sub, 'vector', f'{value.vector()}')
                if isinstance(value, SO):
                    cls._construct_tree_property(sub, 'angle', f'{value.angle()}')
                    cls._construct_tree_property(sub, 'jacobian', f'{value.jacobian()}')
                    cls._construct_tree_property(sub, 'inverse_jacobian', f'{value.inverse_jacobian()}')
                elif isinstance(value, SE):
                    cls._construct_value_tree(sub, 'translation', value.translation())
                    cls._construct_value_tree(sub, 'rotation', value.rotation())
        return sub

    @staticmethod
    def _construct_tree_property(
            root: Item,
            first: str,
            second: str
    ) -> Item:
        item = QtWidgets.QTreeWidgetItem(root)
        item.setText(0, f'{first}:')
        item.setText(1, second)
        item.setFont(1, QtGui.QFont('Courier New', 10))
        item.setToolTip(1, second)
        return item
