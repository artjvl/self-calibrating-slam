from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph.FactorGraph import FactorGraph
from src.framework.types.NodeSE2 import NodeSE2


class EdgeSE2(FactorGraph.Edge):

    tag = 'EDGE_SE2'
    size = 2

    # constructor
    def __init__(self, a, b, transformation=None, information=None):
        assert isinstance(a, NodeSE2)
        assert isinstance(b, NodeSE2)
        if transformation is None:
            transformation = SE2.from_elements(0, 0, 0)
        assert isinstance(transformation, SE2)
        if information is not None:
            assert isinstance(information, Square)
        super().__init__([a, b], transformation, information)

    # public methods
    def get_transformation(self):
        return self.get_value()

    def set_transformation(self, transformation):
        assert isinstance(transformation, SE2)
        self.set_value(transformation)

    # abstract implementations
    def to_string(self):
        data_string = self._elements_to_string(self._array_to_elements(self.get_transformation().vector()))
        if self._is_uncertain:
            data_string += ' {}'.format(self._elements_to_string(self._symmetric_to_elements(self._information)))
        return ' '.join([self.tag, str(self.get_node(0).id()), str(self.get_node(1).id()), data_string])

    def read(self, words):
        assert isinstance(words, list)
        assert all(isinstance(word, str) for word in words)
        elements = [float(word) for word in words]
        if len(elements) != 3:
            self.set_information(self._elements_to_symmetric(elements[3:]))
        self.set_transformation(SE2.from_vector(Vector(elements[: 3])))

    @classmethod
    def from_nodes(cls, nodes):
        assert isinstance(nodes, list)
        assert all(isinstance(node, NodeSE2) for node in nodes)
        return cls(nodes[0], nodes[1])
