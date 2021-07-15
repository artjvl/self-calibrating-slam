from src.framework.graph.types.SuffixDatabase import SuffixDatabase
from src.framework.graph.types.edges.EdgePose2DV2 import EdgePose2DV2
from src.framework.graph.types.edges.EdgePosePoint2DV2 import EdgePosePoint2DV2
from src.framework.graph.types.edges.EdgePoses2DSE2 import EdgePoses2DSE2
from src.framework.graph.types.edges.InformationEdge import InformationEdge2, InformationEdge3
from src.framework.graph.types.nodes.InformationNode import InformationNode2, InformationNode3
from src.framework.graph.types.nodes.NodeSE2 import NodeSE2
from src.framework.graph.types.nodes.NodeV2 import NodeV2
from src.framework.graph.types.nodes.ParameterNode import BiasParameterNode, OffsetParameterNode, \
    ScaleParameterNode

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

database.register_type('PARAM_BIAS', BiasParameterNode)
database.register_type('PARAM_OFFSET', OffsetParameterNode)
database.register_type('PARAM_SCALE', ScaleParameterNode)

# parameter suffixes
database.register_parameter_suffix('BIAS', BiasParameterNode)
database.register_parameter_suffix('OFFSET', OffsetParameterNode)
database.register_parameter_suffix('SCALE', ScaleParameterNode)

# information suffixes
database.register_information_suffix('I2', InformationNode2)
database.register_information_suffix('I3', InformationNode3)
