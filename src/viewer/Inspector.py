from PyQt5.QtWidgets import *  # QMainWindow, QWidget, QDesktopWidget, QAction, qApp, QHBoxLayout
from PyQt5.QtGui import *  # QDesktopServices

from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph import *


class Inspector(QTreeWidget):

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headerItem().setText(0, 'Property')
        self.headerItem().setText(1, 'Value')
        self.setColumnWidth(0, 140)
        self.setAlternatingRowColors(True)

    # helper-methods
    @classmethod
    def construct_node_tree(cls, root, node):
        assert isinstance(node, FactorGraph.Node)

        # tag:
        cls.construct_tree_property(root, 'tag', "'{}'".format(type(node).tag))
        # id:
        cls.construct_tree_property(root, 'id', '{}'.format(node.id()))
        # value:
        cls.construct_value_tree(root, 'value', node.get_value())
        root.expandAll()

    @classmethod
    def construct_edge_tree(cls, root, edge):
        assert isinstance(edge, FactorGraph.Edge)

        # tag:
        cls.construct_tree_property(root, 'tag', "'{}'".format(type(edge).tag))
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
        root.expandAll()

    @classmethod
    def construct_value_tree(cls, root, value_string, value):
        assert isinstance(root, (QTreeWidget, QTreeWidgetItem))
        assert isinstance(value, (Vector, SO, SE))
        if isinstance(value, Vector):
            cls.construct_tree_property(root, value_string, '{}'.format(value))
        else:
            cls.construct_group_tree(root, value_string, value)

    @classmethod
    def construct_group_tree(cls, root, group_string, group):
        assert isinstance(root, (QTreeWidget, QTreeWidgetItem))
        assert isinstance(group_string, str)
        assert isinstance(group, (SO, SE))
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
    def construct_tree_property(root, property_string, value_string):
        assert isinstance(root, (QTreeWidget, QTreeWidgetItem))
        assert isinstance(property_string, str)
        assert isinstance(value_string, str)
        item = QTreeWidgetItem(root)
        item.setText(0, '{}:'.format(property_string))
        item.setText(1, value_string)
        item.setFont(1, QFont('Courier New', 10))
        item.setToolTip(1, value_string)