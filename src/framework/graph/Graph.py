from src.framework.graph.BaseGraph import BaseGraph
from src.framework.types.NodeSE2 import NodeSE2
from src.framework.types.EdgeSE2 import EdgeSE2


class Graph(BaseGraph):

    # constructor
    def __init__(self):
        super().__init__()
        self.types = self.init_types()

    # initialisation
    def init_types(self):
        types = dict()
        types['VERTEX_SE2'] = NodeSE2
        types['EDGE_SE2'] = EdgeSE2
        return types

    # loading / saving
    def load(self, filename):
        print('Reading file: {}'.format(filename))
        file = open(filename, 'r')
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line == '\n':
                raise Exception('Empty line {}'.format(i + 1))
            line = line.strip()
            words = line.split()

            # handle FIX

            token = words[0]
            if token not in self.types:
                raise Exception("Unknown type in line {}: '{}' (only [{}] are known)".format(i + 1, line, ', '.join(self.types.keys())))
            else:
                element_type = self.types[token]

            # handle parameters

            if issubclass(element_type, BaseGraph.Node):
                id = int(words[1])
                node = element_type(id)
                rest = words[2:]
                node.read(rest)
                self.add_node(node)
            elif issubclass(element_type, BaseGraph.Edge):
                size = element_type.size
                ids = words[1: 1 + size]
                nodes = [self.get_node(int(id)) for id in ids]
                edge = element_type.from_nodes(nodes)
                self.add_edge(edge)

    def save(self, filename):
        print('Saving to file: {}'.format(filename))
        file = open(filename, 'x')

        node_set = list()
        edge_set = self.get_edges()
        for edge in edge_set:
            nodes = edge.get_nodes()
            for node in nodes:
                if node not in node_set:
                    node_set.append(node)
        for node in node_set:
            file.write(node.to_string() + '\n')
        for edge in edge_set:
            file.write(edge.to_string() + '\n')
