from src.framework.groups import *
from src.framework.graph.Graph import Graph
from src.framework.graph.types.Type import Type


class NodeSE2(Type, Graph.Node):

    # constructor
    def __init__(self, id, true, estimated):
        assert isinstance(id, int)
        assert isinstance(true, SE2)
        assert isinstance(estimated, SE2)
        super().__init__(id)
        self._true = true
        self._estimated = estimated

    # public methods
    def get_true(self):
        return self._true

    def get_estimated(self):
        return self._estimated

    # abstract implementations
    def id(self) -> str:
        return str(self.get_id())

    def data_to_string(self) -> str:
        return type(self)._array_to_string(self.get_estimated().vector())

    @staticmethod
    def tag() -> str:
        return 'VERTEX_SE2'
