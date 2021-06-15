from src.framework.graph.types.scslam2d.edges.InformationEdge import InformationEdge2, InformationEdge3
from src.framework.graph.types.scslam2d.SuffixDatabase import SuffixDatabase
from src.framework.graph.types.scslam2d.edges.EdgePose2DV2 import EdgePose2DV2
from src.framework.graph.types.scslam2d.edges.EdgePosePoint2DV2 import EdgePosePoint2DV2
from src.framework.graph.types.scslam2d.edges.EdgePoses2DSE2 import EdgePoses2DSE2
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import InformationNode2, InformationNode3
from src.framework.graph.types.scslam2d.nodes.parameter import ParameterNodeSE2, ParameterNodeV3
from src.framework.graph.types.scslam2d.nodes.topological import NodeSE2, NodeV2

database = SuffixDatabase()

# edge-types
database.register_type('CONSTRAINT_POSES2D_SE2', EdgePoses2DSE2)
database.register_type('CONSTRAINT_POSE2D_V2', EdgePose2DV2)
database.register_type('CONSTRAINT_POSEPOINT2D_V2', EdgePosePoint2DV2)
database.register_type('CONSTRAINT_INFO2', InformationEdge2)
database.register_type('CONSTRAINT_INFO3', InformationEdge3)

# node-types
database.register_type('NODE_SE2', NodeSE2)
database.register_type('NODE_V2', NodeV2)

database.register_type('INFO2', InformationNode2)
database.register_type('INFO3', InformationNode3)

database.register_type('PARAM_SE2', ParameterNodeSE2)
database.register_type('PARAM_V3', ParameterNodeV3)

# parameter suffixes
database.register_parameter_suffix('PSE2', ParameterNodeSE2)
database.register_parameter_suffix('PV3', ParameterNodeV3)

# information suffixes
database.register_information_suffix('I2', InformationNode2)
database.register_information_suffix('I3', InformationNode3)
