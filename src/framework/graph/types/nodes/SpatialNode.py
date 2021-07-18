import typing as tp
from abc import abstractmethod

from src.framework.graph.Graph import Node
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.protocols.visualisable.DrawAxis import DrawAxis
from src.framework.graph.protocols.visualisable.DrawPoint import DrawPoint
from src.framework.math.lie.transformation import SE2
from src.framework.math.lie.transformation import SE3
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3

SubSpatialNode = tp.TypeVar('SubSpatialNode', bound='SpatialNode')
T = tp.TypeVar('T')


class SpatialNode(tp.Generic[T], Node[T]):

    @abstractmethod
    def get_translation(self) -> Vector2:
        pass


class NodeV2(SpatialNode[Vector2], DrawPoint):
    _type = Vector2

    def get_translation(self) -> Vector2:
        assert self.has_value()
        return self.get_value()

    def draw_point(self) -> Vector3:
        return self.get_value().to_vector3()


class NodeSE2(SpatialNode[SE2], DrawAxis):
    _type = SE2

    def get_translation(self) -> Vector2:
        assert self.has_value()
        return self.get_value().translation()

    def draw_pose(self) -> SE3:
        return self.get_value().to_se3()

    def compute_ate2(self) -> float:
        assert self.has_true()
        delta: Vector2 = self.get_true().get_value().translation() - self.get_value().translation()
        return delta[0] ** 2 + delta[1] ** 2


class SpatialNodeFactory(object):
    _map: tp.Dict[Supported, tp.Type[SubSpatialNode]] = {
        SE2: NodeSE2,
        Vector2: NodeV2
    }

    @classmethod
    def from_value_type(
            cls,
            value_type: tp.Type[Supported]
    ) -> tp.Type[SubSpatialNode]:
        assert value_type in cls._map, f"Node with value type '{value_type}' not known."
        return cls._map[value_type]

    @classmethod
    def from_value(
            cls,
            value: Supported,
            id_: tp.Optional[int] = None
    ) -> SubSpatialNode:
        node_type: tp.Type[SubSpatialNode] = cls.from_value_type(type(value))
        node: SubSpatialNode = node_type(id_=id_, value=value)
        return node
