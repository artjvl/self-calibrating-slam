import copy

from src.definitions import get_project_root
from src.framework.ppg.GraphParser import GraphParser
from src.framework.ppg.parameter.ParameterNodeFactory import ParameterNodeFactory
from src.framework.ppg.spatial.SpatialNodeFactory import SpatialNodeFactory
from src.framework.ppg.constraint.EdgeFactory import EdgeFactory
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector1
from src.framework.ppg.Graph import Graph
from src.framework.ppg.constraint.EdgePosesSE2 import EdgePosesSE2
from src.framework.ppg.parameter.ParameterNodeV1 import ParameterNodeV1
from src.framework.ppg.parameter.ParameterSpecification import ParameterSpecification
from src.framework.ppg.spatial.NodeSE2 import NodeSE2

g1 = Graph()
n = SpatialNodeFactory.from_value(None, 1, SE2.from_translation_angle_elements(1, 2, 0))
# n = NodeSE2(None, 1, 1, SE2.from_translation_angle_elements(1, 2, 0))
g1.add_node(n)
m = NodeSE2(None, 2, SE2.from_translation_angle_elements(2, 1, 0))
g1.add_node(m)

p = ParameterNodeFactory.from_value(None, 3, Vector1(.1), ParameterSpecification.BIAS, 1)
# p = ParameterNodeV1(None, 3, Vector1(.1), ParameterSpecification.BIAS, 1)

e = EdgeFactory.from_measurement_nodes(None, SE2.from_translation_angle_elements(0, 0, 0), [n, m], Square3.identity())
# e = EdgePosesSE2(None, SE2.from_translation_angle_elements(0, 0, 0), Square3.identity(), n, m)
e.add_node(p)
g1.add_node(p)
g1.add_edge(e)


file = (get_project_root() / 'graphs/temp/after.g2o').resolve()
g = GraphParser.load(file)
h = copy.copy(g)
f = copy.deepcopy(g)
GraphParser.save(f, (get_project_root() / 'graphs/test.g2o').resolve())

print('end')