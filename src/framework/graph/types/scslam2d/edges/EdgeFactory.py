import typing as tp

from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.edges.CalibratingEdge import SubCalibratingEdge
from src.framework.graph.types.scslam2d.edges.EdgePose2DV2 import EdgePose2DV2
from src.framework.graph.types.scslam2d.edges.EdgePosePoint2DV2 import EdgePosePoint2DV2
from src.framework.graph.types.scslam2d.edges.EdgePoses2DSE2 import EdgePoses2DSE2
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import SubCalibratingNode
from src.framework.graph.types.scslam2d.nodes.typological import NodeSE2, NodeV2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2

Key = tp.Tuple[tp.Type[Supported], tp.Tuple[tp.Type[SubCalibratingNode], ...]]


class EdgeFactory(object):
    _map: tp.Dict[
        Key,
        tp.Type[SubCalibratingEdge]
    ] = {
        (SE2, (NodeSE2, NodeSE2)): EdgePoses2DSE2,
        (Vector2, (NodeSE2)): EdgePose2DV2,
        (Vector2, (NodeSE2, NodeV2)): EdgePosePoint2DV2
    }

    @classmethod
    def from_types_measurement_nodes(
            cls,
            measurement_type: tp.Type[Supported],
            *node_types: tp.Type[SubCalibratingNode]
    ) -> tp.Type[SubCalibratingEdge]:
        key: Key = (measurement_type, node_types)
        assert key in cls._map, f"Edge with measurement type '{measurement_type}' and nodes '{node_types}' not known."
        return cls._map[key]

    @classmethod
    def from_measurement_nodes(
            cls,
            measurement: Supported,
            *nodes: SubCalibratingNode
    ) -> SubCalibratingEdge:
        node_types: tp.Tuple[tp.Type[SubCalibratingNode], ...] = tuple(type(node) for node in nodes)
        edge_type: tp.Type[SubCalibratingEdge] = cls.from_types_measurement_nodes(type(measurement), *node_types)
        edge: SubCalibratingEdge = edge_type(*nodes)
        edge.set_measurement(measurement)
        return edge
