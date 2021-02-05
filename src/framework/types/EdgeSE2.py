from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph.BaseGraph import BaseGraph
from src.framework.graph.types.NodeSE2 import NodeSE2


class EdgeSE2(BaseGraph.Edge):

    tag = 'EDGE_SE2'
    size = 2

    # constructor
    def __init__(self, a, b, transformation=None):
        assert isinstance(id, int)
        assert isinstance(a, NodeSE2)
        assert isinstance(b, NodeSE2)
        super().__init__([a, b])
        if transformation is None:
            transformation = SE2.from_elements(0, 0, 0)
        assert isinstance(transformation, SE2)
        self._transformation = transformation

    # public methods
    def get_transformation(self):
        return self._transformation

    def set_transformation(self, transformation):
        assert isinstance(transformation, SE2)
        self._transformation = transformation

    # abstract implementations
    def to_string(self):
        pose_string = self._array_to_string(self._transformation.vector())
        return ' '.join([self.tag, str(self.get_node(0).id()), str(self.get_node(1).id()), pose_string])

    def read(self, words):
        assert isinstance(words, list)
        assert all(isinstance(word, str) for word in words)
        elements = [float(word) for word in words]
        self.set_transformation(SE2.from_vector(Vector(elements)))
