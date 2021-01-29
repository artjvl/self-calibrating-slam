from src.framework.graph.Node import Node
from src.framework.graph.Edge import Edge


class Graph(object):

    # constructor
    def __init__(self):
        self._nodes = dict()
        self._edges = dict()

    # public methods
    def get_node(self, id):
        assert isinstance(id, int)
        if id in self._nodes:
            return self._nodes[id]
        else:
            return None

    def add_node(self, node):
        assert isinstance(node, Node)
        self._nodes[node.get_id()] = node

    def get_edge(self, id):
        assert isinstance(id, int)
        if id in self._edges:
            return self._edges[id]
        else:
            return None

    def add_edge(self, edge):
        assert isinstance(edge, Edge)
        self._edges[edge.get_id()] = edge
