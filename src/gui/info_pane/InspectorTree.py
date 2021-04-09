import typing as tp

from PyQt5 import QtGui, QtWidgets

from src.framework.graph.FactorGraph import SubEdge, SubNode, SubGraph, SubElement
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
        self.setColumnWidth(0, 128)
        self.setAlternatingRowColors(True)

    # helper-methods
    @classmethod
    def construct_graph_tree(
            cls,
            root: Item,
            graph: SubGraph
    ):
        sub_elements = QtWidgets.QTreeWidgetItem(root)
        sub_elements.setText(0, 'Elements:')
        element_type: tp.Type[SubElement]
        for element_type in graph.get_types():
            cls.construct_tree_property(sub_elements, f"size '{element_type.__name__}'", f'{len(graph.get_of_type(element_type))}')
        cls.construct_tree_property(root, 'error', '{}'.format(graph.compute_error()))
        root.expandAll()

    @classmethod
    def construct_node_tree(
            cls,
            root: Item,
            node: SubNode
    ):
        cls.construct_tree_property(root, 'id', f'{node.get_id()}')
        cls.construct_tree_property(root, 'is_fixed', f'{node.is_fixed()}')
        if isinstance(node, CalibratingNode):
            if isinstance(node, ParameterNode):
                cls.construct_tree_property(root, 'interpretation', f'{node.get_interpretation()}')
            elif isinstance(node, InformationNode):
                cls.construct_tree_property(root, 'matrix', f'{node.get_matrix()}')
        sub_value: Item = cls.construct_value_tree(root, 'value', node.get_value())
        sub_value.setExpanded(True)
        # root.expandAll()

    @classmethod
    def construct_edge_tree(
            cls,
            root: Item,
            edge: SubEdge
    ):
        sub_nodes: Item = QtWidgets.QTreeWidgetItem(root)
        sub_nodes.setText(0, 'nodes:')
        nodes = edge.get_nodes()
        sub_nodes.setText(1, '({})'.format(len(nodes)))
        for i, node in enumerate(nodes):
            cls.construct_tree_property(sub_nodes, f'{i}', f'{node.to_unique()}')
        sub_nodes.setExpanded(True)

        cls.construct_tree_property(root, 'cardinality', f'{edge.get_cardinality()}')
        cls.construct_tree_property(root, 'information', f'{edge.get_information()}')
        cls.construct_tree_property(root, 'error_vector', f'{edge.compute_error_vector()}')
        cls.construct_tree_property(root, 'error', f'{edge.compute_error()}')

        # if isinstance(edge, CalibratingEdge):
        #

        sub_measurement: Item = cls.construct_value_tree(root, 'measurement', edge.get_measurement())
        sub_measurement.setExpanded(True)
        sub_estimate: Item = cls.construct_value_tree(root, 'estimate', edge.get_estimate())
        sub_estimate.setExpanded(True)
        # root.expandAll()

    @classmethod
    def construct_value_tree(
            cls,
            root: Item,
            name: str,
            value: Supported
    ) -> Item:
        sub = QtWidgets.QTreeWidgetItem(root)
        sub.setText(0, f'{name}:')
        sub.setText(1, f'{type(value).__name__}')
        cls.construct_tree_property(sub, 'value', f'{value}')
        if isinstance(value, Dimensional):
            cls.construct_tree_property(sub, 'dimension', f'{value.get_dimension()}')
            if isinstance(value, Lie):
                cls.construct_tree_property(sub, 'dof', f'{value.get_dof()}')
                cls.construct_tree_property(sub, 'vector', f'{value.vector()}')
                if isinstance(value, SO):
                    cls.construct_tree_property(sub, 'angle', f'{value.angle()}')
                    cls.construct_tree_property(sub, 'jacobian', f'{value.jacobian()}')
                    cls.construct_tree_property(sub, 'inverse_jacobian', f'{value.inverse_jacobian()}')
                elif isinstance(value, SE):
                    cls.construct_value_tree(sub, 'translation', value.translation())
                    cls.construct_value_tree(sub, 'rotation', value.rotation())
        return sub

    @staticmethod
    def construct_tree_property(
            root: Item,
            property_string: str,
            value_string: str
    ):
        item = QtWidgets.QTreeWidgetItem(root)
        item.setText(0, '{}:'.format(property_string))
        item.setText(1, value_string)
        item.setFont(1, QtGui.QFont('Courier New', 10))
        item.setToolTip(1, value_string)
