from src.framework.groups import *
from src.framework.structures import *
from src.framework.graph.types.Type import Type
from src.framework.graph.Graph import Graph


class EdgeSE2(Type, Graph.Edge):

    # constructor
    def __init__(self, id, transformation, information, nodes=None):
        assert isinstance(id, int)
        assert isinstance(transformation, SE2)
        assert isinstance(information, Square)
        super().__init__(id, nodes)
        self._transformation = transformation
        self._information = information

    # public methods
    def get_transformation(self):
        return self._transformation

    def get_information(self):
        return self._information

    # abstract implementations
    def id(self):
        return self.get_id()

    def data_to_string(self):
        return type(self)._array_to_string(self.get_information())

    @staticmethod
    def tag():
        return 'EDGE_SE2'
