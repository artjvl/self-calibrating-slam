import pathlib
from typing import *

from src.framework.graph.factor import *
from src.framework.graph.types import *


class Graph(FactorGraph):

    # constructor
    def __init__(self, id: Optional[int] = 0, name: Optional[str] = None):
        super().__init__()
        self.types = self.init_types()
        self._id = id
        self._name = name

    # initialisation
    def init_types(self) -> dict:
        types = dict()
        types['VERTEX_SE2'] = NodeSE2
        types['EDGE_SE2'] = EdgeSE2
        types['VERTEX_POINT_XY'] = NodeXY
        types['EDGE_SE2_POINT_XY'] = EdgeSE2XY
        return types

    # public methods
    def get_id(self) -> int:
        return self._id

    def set_id(self, id: int):
        self._id = id

    def get_name(self, short: bool = False):
        if self._name is None:
            return self.__repr__()
        else:
            if short:
                return pathlib.Path(self._name).name
            return self._name

    # loading / saving
    def load(self, filename: str):
        self._name = filename
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

            if issubclass(element_type, FactorNode):
                id = int(words[1])
                node = element_type(id)
                rest = words[2:]
                node.read(rest)
                self.add_node(node)
            elif issubclass(element_type, FactorEdge):
                size = element_type.size
                ids = words[1: 1 + size]
                nodes = [self.get_node(int(id)) for id in ids]
                edge = element_type.from_nodes(nodes)
                rest = words[1 + size:]
                edge.read(rest)
                self.add_edge(edge)

    def save(self, filename: str):
        self._name = filename
        print('Saving to file: {}'.format(filename))
        file = pathlib.Path(filename)
        if file.exists():
            file.unlink()
        file = open(filename, 'x')

        for node in self.get_nodes():
            file.write(node.write() + '\n')
        for edge in self.get_edges():
            file.write(edge.write() + '\n')
