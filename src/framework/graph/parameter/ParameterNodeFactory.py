import typing as tp

from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector1, Vector2, Vector3
from src.framework.graph.Graph import SubParameterNode
from src.framework.graph.parameter.ParameterNodeSE2 import ParameterNodeSE2
from src.framework.graph.parameter.ParameterNodeV1 import ParameterNodeV1
from src.framework.graph.parameter.ParameterNodeV2 import ParameterNodeV2
from src.framework.graph.parameter.ParameterNodeV3 import ParameterNodeV3
from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification

if tp.TYPE_CHECKING:
    from src.framework.graph.data.DataFactory import Quantity


class ParameterNodeFactory(object):
    _map: tp.Dict['Quantity', tp.Type[SubParameterNode]] = {
        SE2: ParameterNodeSE2,
        Vector1: ParameterNodeV1,
        Vector2: ParameterNodeV2,
        Vector3: ParameterNodeV3
    }

    @classmethod
    def from_value_type(
            cls,
            value_type: tp.Type['Quantity']
    ) -> tp.Type[SubParameterNode]:
        assert value_type in cls._map, f'{value_type}'
        return cls._map[value_type]

    @classmethod
    def from_value(
            cls,
            name: tp.Optional[str],
            value: 'Quantity',
            specification: tp.Optional[ParameterSpecification] = None,
            id_: int = 0,
            timestep: int = 0,
            index: int = 0
    ) -> SubParameterNode:
        node_type: tp.Type[SubParameterNode] = cls.from_value_type(type(value))
        node: SubParameterNode = node_type(
            name,
            id_=id_, value=value, specification=specification, timestep=timestep, index=index
        )
        return node
