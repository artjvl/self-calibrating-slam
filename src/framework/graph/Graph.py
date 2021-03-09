import pathlib
from datetime import datetime
from typing import *

from src.framework.graph.factor.FactorEdge import FactorEdge
from src.framework.graph.factor.FactorGraph import FactorGraph
from src.framework.graph.factor.FactorNode import FactorNode
from src.framework.graph.types import *


class Graph(FactorGraph):

    # constructor
    def __init__(self, id: Optional[int] = 0, name: Optional[str] = None):
        super().__init__()
        self._types = self._init_types()
        self._id = id
        self._file: Optional[pathlib.Path] = None
        self._date: datetime = datetime.now()

    # initialisation
    @staticmethod
    def _init_types() -> Dict[str, Any]:
        types: Dict[str, Any] = dict()
        types['VERTEX_SE2'] = NodeSE2
        types['EDGE_SE2'] = EdgeSE2
        types['VERTEX_XY'] = NodeXY
        types['EDGE_SE2_XY'] = EdgeSE2XY
        return types

    # getters/setters
    def get_id(self) -> int:
        assert self._id is not None
        return self._id

    def set_id(self, id: int):
        self._id = id

    def get_file_name(self, short: bool = False) -> str:
        assert self._file is not None
        if short:
            return str(self._file.name)
        return str(self._file)

    def get_date_name(self, short: bool = False) -> str:
        timestamp: str
        if short:
            timestamp = self._date.strftime('%M%S')
            return 'G-{}-{}'.format(self.get_id(), timestamp)
        else:
            timestamp = self._date.strftime('%Y-%m-%d %H:%M:%S')
            return 'Graph (id: {}, time: {})'.format(self.get_id(), timestamp)

    def get_name(self, short: bool = False) -> str:
        if self._file is None:
            return self.get_date_name(short)
        else:
            return self.get_file_name(short)

    # load/save methods
    def load(self, file: pathlib.Path):
        self._file = file
        print('Reading file: {}'.format(str(file)))
        reader = file.open('r')
        lines = reader.readlines()
        for i, line in enumerate(lines):
            assert line != '\n', 'Empty line {}'.format(i + 1)
            line = line.strip()
            words = line.split()

            token = words[0]

            if token == 'FIX':
                id = int(words[1])
                assert self.contains_node(id)
                node = self.get_node(id)
                node.set_fixed()
            else:
                assert token in self._types, 'unknown token: {}'.format(token)
                element_type = self._types[token]

                # handle parameters

                if issubclass(element_type, FactorNode):
                    id = int(words[1])
                    node = element_type(id)
                    rest = words[2:]
                    node.read(rest)
                    self.add_node(node)
                elif issubclass(element_type, FactorEdge):
                    size = element_type.cardinality
                    ids = words[1: 1 + size]
                    nodes = [self.get_node(int(id)) for id in ids]
                    assert all(self.contains_node(node.get_id()) for node in self.get_nodes())
                    edge = element_type.from_nodes(nodes)
                    rest = words[1 + size:]
                    edge.read(rest)
                    self.add_edge(edge)

    def save(self, file: pathlib.Path):
        self._file = file
        print('Saving to file: {}'.format(str(file)))
        if file.exists():
            file.unlink()
        writer = file.open('x')

        for node in self.get_nodes():
            writer.write('{}\n'.format(node.write()))
            if node.is_fixed():
                writer.write('FIX {}\n'.format(node.get_id()))
        for edge in self.get_edges():
            writer.write('{}\n'.format(edge.write()))

    # object methods
    def __str__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.get_id(), self.id_string())