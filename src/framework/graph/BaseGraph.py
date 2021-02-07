class BaseGraph(object):

    # subclass: BaseNode
    class BaseNode(object):

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

        def __repr__(self):
            return '{}({})'.format(self.__class__.__name__, self.id())

    # subclass: BaseEdge
    class BaseEdge(object):

        # constructor
        def __init__(self, nodes):
            assert isinstance(nodes, list)
            assert all(isinstance(node, BaseGraph.BaseNode) for node in nodes)
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

        def __repr__(self):
            return '{}({})'.format(self.__class__.__name__, ', '.join([str(node.id()) for node in self.get_nodes()]))

    # constructor
    def __init__(self):
        self._nodes = dict()
        self._edges = list()

    # public methods
    def get_nodes(self):
        return self._nodes.values()

    def get_node(self, id):
        assert isinstance(id, int)
        if id in self._nodes:
            return self._nodes[id]
        raise Exception('No node found with id {}'.format(id))
        # return None

    def add_node(self, node):
        assert isinstance(node, self.BaseNode)
        self._nodes[node.id()] = node

    def get_edges(self):
        return self._edges

    def get_edge(self, index):
        assert isinstance(index, int)
        assert index < len(self._edges)
        return self._edges[index]

    def add_edge(self, edge):
        assert isinstance(edge, self.BaseEdge)
        if edge not in self._edges:
            self._edges.append(edge)
