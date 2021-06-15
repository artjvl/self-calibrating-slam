import typing as tp

from src.framework.graph.FactorGraph import SubFactorNode
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.nodes.topological.NodeSE2 import NodeSE2
from src.framework.graph.types.scslam2d.nodes.topological.NodeV2 import NodeV2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2


class NodeFactory(object):
    _map: tp.Dict[
        Supported,
        tp.Type[SubFactorNode]
    ] = {
        SE2: NodeSE2,
        Vector2: NodeV2
    }

    @classmethod
    def from_value_type(
            cls,
            value_type: tp.Type[Supported]
    ) -> tp.Type[SubFactorNode]:
        assert value_type in cls._map, f"Node with value type '{value_type}' not known."
        return cls._map[value_type]

    @classmethod
    def from_value(
            cls,
            value: Supported,
            id_: int = 0
    ) -> SubFactorNode:
        node_type: tp.Type[SubFactorNode] = cls.from_value_type(type(value))
        node: SubFactorNode = node_type(id_, value)
        return node
