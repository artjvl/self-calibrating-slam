from abc import ABC

from src.framework.graph.types.Type import Type


class Graph(object):

    # subclass: Node
    class Node(Type, ABC):

        def __init__(self, id, edges=None):
            assert isinstance(id, int)
            super().__init__(id)
            if edges is None:
                self._edges = []
            else:
                assert isinstance(edges, list)
                self._edges = edges

        # public methods
        def get_edges(self):
            return self._edges

        def get_edge(self, index):
            assert isinstance(index, int)
            if index < len(self._edges):
                return self._edges[index]
            else:
                return None

        def add_edge(self, edge):
            assert isinstance(edge, Graph.Edge)
            if edge not in self._edges:
                self._edges.append(edge)

    # subclass: Edge
    class Edge(Type, ABC):

        def __init__(self, id, nodes=None):
            assert isinstance(id, int)
            super().__init__(id)
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

        def add_nodes(self, *args):
            for node in args:
                assert isinstance(node, Graph.Node)
                if node not in self._nodes:
                    self._nodes.append(node)

    # constructor
    def __init__(self):
        self.types = dict()
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
        assert isinstance(node, self.Node)
        self._nodes[node.get_id()] = node

    def get_edge(self, id):
        assert isinstance(id, int)
        if id in self._edges:
            return self._edges[id]
        else:
            return None

    def add_edge(self, edge):
        assert isinstance(edge, self.Edge)
        self._edges[edge.get_id()] = edge

    def load(self, filename):
        file = open(filename, 'r')
        lines = file.readlines()
        for line in lines:
            words = line.strip()
            # handle FIX
            token = words[0]
            if token not in self.types:
                raise Exception('Wrong type!')
            else:
                element_type = self.types[token]
            # handle parameters
            id = words[1]
            rest = words[2:]
            element = element_type(id, rest)
