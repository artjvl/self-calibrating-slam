from typing import *

from PyQt5.QtGui import *  # QDesktopServices
from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout

from src.framework.graph import Graph
from src.framework.graph.factor import FactorNode, FactorEdge
from src.framework.groups import SO3
from src.framework.groups.SE import SE
from src.framework.groups.SO import SO
from src.framework.structures import *


class InspectorTree(QTreeWidget):

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
            root: Union[QTreeWidget, QTreeWidgetItem],
            graph: Graph
    ):
        cls.construct_tree_property(root, 'dimensionality', '{}'.format(graph.get_dimensionality()))
        cls.construct_tree_property(root, 'is_uncertain', '{}'.format(graph.is_uncertain()))
        cls.construct_tree_property(root, 'error', '{}'.format(graph.compute_error()))

    @classmethod
    def construct_node_tree(
            cls,
            root: Union[QTreeWidget, QTreeWidgetItem],
            node: FactorNode
    ):
        # static properties:
        cls.construct_tree_property(root, 'tag', "'{}'".format(type(node).tag))
        cls.construct_tree_property(root, 'dimensionality', '{}'.format(type(node).dimensionality))
        cls.construct_tree_property(root, 'is_physical', '{}'.format(type(node).is_physical))
        cls.construct_tree_property(root, 'has_rotation', '{}'.format(type(node).has_rotation))
        # id:
        cls.construct_tree_property(root, 'id', '{}'.format(node.get_id()))
        # value:
        cls.construct_value_tree(root, 'value', node.get_value())
        root.expandAll()

    @classmethod
    def construct_edge_tree(
            cls,
            root: Union[QTreeWidget, QTreeWidgetItem],
            edge: FactorEdge
    ):
        # tag:
        cls.construct_tree_property(root, 'tag', "'{}'".format(type(edge).tag))
        cls.construct_tree_property(root, 'cardinality', '{}'.format(type(edge).cardinality))
        cls.construct_tree_property(root, 'dimensionality', '{}'.format(type(edge).dimensionality))
        cls.construct_tree_property(root, 'is_physical', '{}'.format(type(edge).is_physical))
        # nodes:
        tree_nodes = QTreeWidgetItem(root)
        tree_nodes.setText(0, 'nodes:')
        nodes = edge.get_nodes()
        tree_nodes.setText(1, '({})'.format(len(nodes)))
        for i, node in enumerate(nodes):
            cls.construct_tree_property(tree_nodes, '{}'.format(i), '{}'.format(node))
        # value:
        cls.construct_value_tree(root, 'value', edge.get_value())
        if edge.is_uncertain():
            # information:
            cls.construct_tree_property(root, 'information', '{}'.format(edge.get_information()))
        # error:
        cls.construct_tree_property(root, 'error', '{}'.format(edge.compute_error_vector()))
        root.expandAll()

    @classmethod
    def construct_value_tree(
            cls,
            root: Union[QTreeWidget, QTreeWidgetItem],
            value_string: str,
            value: Union[Vector, SO, SE]
    ):
        if isinstance(value, Vector):
            cls.construct_tree_property(root, value_string, '{}'.format(value))
        else:
            cls.construct_group_tree(root, value_string, value)

    @classmethod
    def construct_group_tree(
            cls,
            root: Union[QTreeWidget, QTreeWidgetItem],
            group_string: str,
            group: Union[SO, SE]
    ):
        values = QTreeWidgetItem(root)
        values.setText(0, group_string)
        # vector:
        cls.construct_tree_property(values, 'vector', '{}'.format(group.vector()))
        # matrix:
        cls.construct_tree_property(values, 'matrix', '{}'.format(group.matrix()))
        counter = 2
        if isinstance(group, SO):
            cls.construct_tree_property(values, 'angle', '{}'.format(group.angle()))
            counter += 1
            if isinstance(group, SO3):
                cls.construct_tree_property(values, 'quaternion', '{}'.format(group.quaternion()))
                cls.construct_tree_property(values, 'euler', '{}'.format(group.euler()))
                counter += 2
        elif isinstance(group, SE):
            translation = group.translation()
            cls.construct_tree_property(values, 'translation', '{}'.format(translation))
            rotation = group.rotation()
            cls.construct_group_tree(values, 'rotation', rotation)
            counter += 2
        values.setText(1, '({})'.format(counter))

    @staticmethod
    def construct_tree_property(
            root: Union[QTreeWidget, QTreeWidgetItem],
            property_string: str,
            value_string: str
    ):
        item = QTreeWidgetItem(root)
        item.setText(0, '{}:'.format(property_string))
        item.setText(1, value_string)
        item.setFont(1, QFont('Courier New', 10))
        item.setToolTip(1, value_string)
