from src.framework.graph.Database import Database
from src.framework.graph.constraint.EdgePosePointV2 import EdgePosePointV2
from src.framework.graph.constraint.EdgePoseV2 import EdgePoseV2
from src.framework.graph.constraint.EdgePosesSE2 import EdgePosesSE2
from src.framework.graph.parameter.ParameterNodeSE2 import ParameterNodeSE2
from src.framework.graph.parameter.ParameterNodeV1 import ParameterNodeV1
from src.framework.graph.parameter.ParameterNodeV2 import ParameterNodeV2
from src.framework.graph.parameter.ParameterNodeV3 import ParameterNodeV3
from src.framework.graph.spatial.NodeSE2 import NodeSE2
from src.framework.graph.spatial.NodeV2 import NodeV2

database = Database()

# edge-types
database.register_type('CONSTRAINT_POSES2D_SE2', EdgePosesSE2)
database.register_type('CONSTRAINT_POSE2D_V2', EdgePoseV2)
database.register_type('CONSTRAINT_POSEPOINT2D_V2', EdgePosePointV2)

# node-types
database.register_type('NODE_SE2', NodeSE2)
database.register_type('NODE_V2', NodeV2)

database.register_type('PARAMETER_SE2', ParameterNodeSE2)
database.register_type('PARAMETER_V1', ParameterNodeV1)
database.register_type('PARAMETER_V2', ParameterNodeV2)
database.register_type('PARAMETER_V3', ParameterNodeV3)

# parameter suffixes
database.register_parameter_suffix('SE2', ParameterNodeSE2)
database.register_parameter_suffix('V1', ParameterNodeV1)
database.register_parameter_suffix('V2', ParameterNodeV2)
database.register_parameter_suffix('V3', ParameterNodeV3)
