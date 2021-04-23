import typing as tp

from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import SubCalibratingNode
from src.framework.graph.types.scslam2d.nodes.topological import NodeSE2, NodeV2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2


class NodeFactory(object):
    _map: tp.Dict[
        Supported,
        tp.Type[SubCalibratingNode]
    ] = {
        SE2: NodeSE2,
        Vector2: NodeV2
    }

    @classmethod
    def from_value_type(
            cls,
            value_type: tp.Type[Supported]
    ) -> tp.Type[SubCalibratingNode]:
        assert value_type in cls._map, f"Node with value type '{value_type}' not known."
        return cls._map[value_type]

    @classmethod
    def from_value(
            cls,
            value: Supported,
            id_: int = 0
    ) -> SubCalibratingNode:
        node_type: tp.Type[SubCalibratingNode] = cls.from_value_type(type(value))
        node: SubCalibratingNode = node_type(id_, value)
        return node
