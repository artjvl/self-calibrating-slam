from abc import ABC, abstractmethod

from src.framework.graph.Element import Element


class BaseGraph(object):

    # subclass: Node
    class Node(Element, ABC):

        # constructor
        def __init__(self, id):
            assert isinstance(id, int)
            self._id = id

        # public methods
        def id(self):
            return self._id

        def set_id(self, id):
            assert isinstance(id, int)
            self._id = id

    # subclass: Edge
    class Edge(Element, ABC):

        # constructor
        def __init__(self, nodes):
            assert isinstance(nodes, list)
            assert all(isinstance(node, BaseGraph.Node) for node in nodes)
            self._nodes = nodes

        # public methods
        def get_nodes(self):
            return self._nodes

        def get_node(self, index):
            assert isinstance(index, int)
            if index < len(self._nodes):
                return self._nodes[index]
            raise Exception('No node found at index {}'.format(index))
            # return None

        # abstract properties
        @property
        @classmethod
        @abstractmethod
        def size(cls):
            pass

        # abstract methods
        @classmethod
        @abstractmethod
        def from_nodes(cls, nodes):
            pass

    # constructor
    def __init__(self):
        self._nodes = dict()
        self._edges = list()

    # public methods
    def get_nodes(self):
        return self._nodes

    def get_node(self, id):
        assert isinstance(id, int)
        if id in self._nodes:
            return self._nodes[id]
        raise Exception('No node found with id {}'.format(id))
        # return None

    def add_node(self, node):
        assert isinstance(node, self.Node)
        self._nodes[node.id()] = node

    def get_edges(self):
        return self._edges

    def get_edge(self, index):
        assert isinstance(index, int)
        assert index < len(self._edges)
        return self._edges[index]

    def add_edge(self, edge):
        assert isinstance(edge, self.Edge)
        if edge not in self._edges:
            self._edges.append(edge)
