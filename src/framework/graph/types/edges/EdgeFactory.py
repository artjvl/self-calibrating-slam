import typing as tp

from src.framework.graph.CalibratingGraph import SubCalibratingEdge, SubCalibratingNode
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.edges.EdgePose2DV2 import EdgePose2DV2
from src.framework.graph.types.edges.EdgePosePoint2DV2 import EdgePosePoint2DV2
from src.framework.graph.types.edges.EdgePoses2DSE2 import EdgePoses2DSE2
from src.framework.graph.types.nodes.SpatialNode import NodeSE2
from src.framework.graph.types.nodes.SpatialNode import NodeV2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import Vector2

Key = tp.Tuple[tp.Type[Supported], tp.Tuple[tp.Type[SubCalibratingNode], ...]]


class EdgeFactory(object):
    _map: tp.Dict[
        Key,
        tp.Type[SubCalibratingEdge]
    ] = {
        (SE2, (NodeSE2, NodeSE2)): EdgePoses2DSE2,
        (Vector2, (NodeSE2, )): EdgePose2DV2,
        (Vector2, (NodeSE2, NodeV2)): EdgePosePoint2DV2
    }

    @classmethod
    def from_types_measurement_nodes(
            cls,
            measurement_type: tp.Type[Supported],
            node_types: tp.List[tp.Type[SubCalibratingNode]]
    ) -> tp.Type[SubCalibratingEdge]:
        key: Key = (measurement_type, tuple(node_types))
        assert key in cls._map, f"Edge with measurement type '{measurement_type}' and nodes '{node_types}' not known."
        return cls._map[key]

    @classmethod
    def from_measurement_nodes(
            cls,
            measurement: Supported,
            nodes: tp.List[SubCalibratingNode],
            name: tp.Optional[str] = None,
            info_matrix: tp.Optional[SubSquare] = None
    ) -> SubCalibratingEdge:
        edge_type: tp.Type[SubCalibratingEdge] = cls.from_types_measurement_nodes(type(measurement), [type(node) for node in nodes])
        edge: SubCalibratingEdge = edge_type(
            name=name,
            nodes=nodes,
            measurement=measurement,
            info_matrix=info_matrix
        )
        return edge
