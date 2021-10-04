import typing as tp

from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.graph.constraint.EdgePosePointV2 import EdgePosePointV2
from src.framework.graph.constraint.EdgePoseV2 import EdgePoseV2
from src.framework.graph.constraint.EdgePosesSE2 import EdgePosesSE2
from src.framework.graph.spatial.NodeSE2 import NodeSE2
from src.framework.graph.spatial.NodeV2 import NodeV2

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubEdge, SubNode
    from src.framework.math.matrix.square import SubSquare
    from src.framework.graph.data.DataFactory import Quantity

Key = tp.Tuple[tp.Type['Quantity'], tp.Tuple[tp.Type['SubNode'], ...]]


class EdgeFactory(object):
    _map: tp.Dict[Key, tp.Type['SubEdge']] = {
        (SE2, (NodeSE2, NodeSE2)): EdgePosesSE2,
        (Vector2, (NodeSE2, )): EdgePoseV2,
        (Vector2, (NodeSE2, NodeV2)): EdgePosePointV2
    }

    @classmethod
    def from_types_measurement_nodes(
            cls,
            measurement_type: tp.Type['Quantity'],
            node_types: tp.List[tp.Type['SubNode']]
    ) -> tp.Type['SubEdge']:
        key: Key = (measurement_type, tuple(node_types))
        assert key in cls._map, f"Edge with measurement type '{measurement_type}' and nodes '{node_types}' not known."
        return cls._map[key]

    @classmethod
    def from_measurement_nodes(
            cls,
            name: tp.Optional[str],
            value: 'Quantity',
            nodes: tp.List['SubNode'],
            info_matrix: tp.Optional['SubSquare'] = None
    ) -> 'SubEdge':
        edge_type: tp.Type['SubEdge'] = cls.from_types_measurement_nodes(type(value), [type(node) for node in nodes])
        edge: 'SubEdge' = edge_type(
            name,
            value=value, info_matrix=info_matrix)
        for node in nodes:
            edge.add_node(node)
        return edge
