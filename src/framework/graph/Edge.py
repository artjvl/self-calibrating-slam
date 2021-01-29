from src.framework.graph.Node import Node


class Edge(object):

    # constructor
    def __init__(self, id, nodes=None):
        assert isinstance(id, int)
        self._id = id
        if nodes is None:
            self._nodes = []
        else:
            assert isinstance(nodes, list)
            self._nodes = nodes

    def get_id(self):
        return self._id

    def get_nodes(self):
        return self._nodes

    def get_node(self, index):
        assert isinstance(index, int)
        if index < len(self._nodes):
            return self._nodes[index]
        else:
            return None

    def add_node(self, node):
        assert isinstance(node, Node)
        if node not in self._nodes:
            self._nodes.append(node)
