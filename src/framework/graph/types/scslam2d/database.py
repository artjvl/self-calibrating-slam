from src.framework.graph.types.scslam2d.SuffixDatabase import SuffixDatabase
from src.framework.graph.types.scslam2d.edges.EdgePoses2DSE2 import EdgePoses2DSE2
from src.framework.graph.types.scslam2d.nodes.InformationNodeV3 import InformationNodeV3
from src.framework.graph.types.scslam2d.nodes.NodeSE2 import NodeSE2
from src.framework.graph.types.scslam2d.nodes.ParameterNodeSE2 import ParameterNodeSE2
from src.framework.graph.types.scslam2d.nodes.ParameterNodeV3 import ParameterNodeV3
from src.framework.groups import SE2
from src.framework.structures import Vector2, Vector3

database = SuffixDatabase()

# edge-types
database.register_type('CONSTRAINT_POSES2D_SE2', EdgePoses2DSE2)

# node-types
database.register_type('NODE_SE2', NodeSE2)
database.register_type('PARAM_SE2', ParameterNodeSE2)
database.register_type('PARAM_V3', ParameterNodeV3)
database.register_type('INFO_V3', InformationNodeV3)

# data suffixes
database.register_data_suffix('SE2', SE2)
database.register_data_suffix('V2', Vector2)
database.register_data_suffix('V3', Vector3)

# parameter suffixes
database.register_parameter_suffix('PSE2', SE2)
database.register_parameter_suffix('PV3', Vector3)

# information suffixes
database.register_information_suffix('C3', Vector3)
