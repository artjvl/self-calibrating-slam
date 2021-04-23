from src.framework.graph.types.scslam2d.SuffixDatabase import SuffixDatabase
from src.framework.graph.types.scslam2d.edges.EdgePose2DV2 import EdgePose2DV2
from src.framework.graph.types.scslam2d.edges.EdgePosePoint2DV2 import EdgePosePoint2DV2
from src.framework.graph.types.scslam2d.edges.EdgePoses2DSE2 import EdgePoses2DSE2
from src.framework.graph.types.scslam2d.nodes.information import \
    InformationNodeDiagonal2, InformationNodeDiagonal3, InformationNodeFull2, InformationNodeFull3
from src.framework.graph.types.scslam2d.nodes.parameter import ParameterNodeSE2, ParameterNodeV3
from src.framework.graph.types.scslam2d.nodes.topological import NodeSE2, NodeV2

database = SuffixDatabase()

# edge-types
database.register_type('CONSTRAINT_POSES2D_SE2', EdgePoses2DSE2)
database.register_type('CONSTRAINT_POSE2D_V2', EdgePose2DV2)
database.register_type('CONSTRAINT_POSEPOINT2D_V2', EdgePosePoint2DV2)

# node-types
database.register_type('NODE_SE2', NodeSE2)
database.register_type('NODE_V2', NodeV2)

database.register_type('INFO_D2', InformationNodeDiagonal2)
database.register_type('INFO_D3', InformationNodeDiagonal3)
database.register_type('INFO_F2', InformationNodeFull2)
database.register_type('INFO_F3', InformationNodeFull3)

database.register_type('PARAM_SE2', ParameterNodeSE2)
database.register_type('PARAM_V3', ParameterNodeV3)

# parameter suffixes
database.register_parameter_suffix('PSE2', ParameterNodeSE2)
database.register_parameter_suffix('PV3', ParameterNodeV3)

# information suffixes
database.register_information_suffix('ID2', InformationNodeDiagonal2)
database.register_information_suffix('ID3', InformationNodeDiagonal3)
database.register_information_suffix('IF2', InformationNodeFull2)
database.register_information_suffix('IF3', InformationNodeFull3)
