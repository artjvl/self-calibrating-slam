import typing as tp

from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.graph.Graph import SubSpatialNode
from src.framework.graph.spatial.NodeSE2 import NodeSE2
from src.framework.graph.spatial.NodeV2 import NodeV2

if tp.TYPE_CHECKING:
    from src.framework.graph.data.DataFactory import Quantity


class SpatialNodeFactory(object):
    _map: tp.Dict['Quantity', tp.Type[SubSpatialNode]] = {
        SE2: NodeSE2,
        Vector2: NodeV2
    }

    @classmethod
    def from_value_type(
            cls,
            value_type: tp.Type['Quantity']
    ) -> tp.Type[SubSpatialNode]:
        assert value_type in cls._map, value_type
        return cls._map[value_type]

    @classmethod
    def from_value(
            cls,
            name: tp.Optional[str],
            value: 'Quantity',
            id_: int = 0,
            timestep: int = 0
    ) -> SubSpatialNode:
        node_type: tp.Type[SubSpatialNode] = cls.from_value_type(type(value))
        node: SubSpatialNode = node_type(
            name,
            value=value, id_=id_, timestep=timestep
        )
        return node
