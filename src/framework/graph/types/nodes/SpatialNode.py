import typing as tp
from abc import abstractmethod

from src.framework.graph.Graph import Node
from src.framework.graph.data.DataFactory import Quantity
from src.framework.graph.protocols.Measurement import Measurement2D
from src.framework.graph.protocols.Visualisable import DrawPoint, DrawAxis
from src.framework.math.lie.transformation import SE2
from src.framework.math.lie.transformation import SE3
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3

if tp.TYPE_CHECKING:
    from src.framework.graph.protocols.Measurement import SubMeasurement

SubSpatialNode = tp.TypeVar('SubSpatialNode', bound='SpatialNode')
T = tp.TypeVar('T')


class SpatialNode(tp.Generic[T], Node[T]):

    @abstractmethod
    def get_translation(self) -> Vector2:
        pass

    def has_measurement(self) -> bool:
        return super().has_value()

    @abstractmethod
    def get_measurement(self) -> 'SubMeasurement':
        pass

    @abstractmethod
    def set_measurement(self, measurement: 'SubMeasurement') -> None:
        pass


class NodeV2(SpatialNode[Vector2], DrawPoint):
    _type = Vector2

    def get_translation(self) -> Vector2:
        assert self.has_value()
        return self.get_value()

    def get_measurement(self) -> Measurement2D:
        return Measurement2D.from_translation(self.get_value())

    def set_measurement(self, measurement: Measurement2D) -> None:
        self.set_value(measurement.translation())

    def draw_point(self) -> Vector3:
        return self.get_value().to_vector3()


class NodeSE2(SpatialNode[SE2], DrawAxis):
    _type = SE2

    def get_translation(self) -> Vector2:
        assert self.has_value()
        return self.get_value().translation()

    def has_measurement(self) -> bool:
        return super().has_value()

    def get_measurement(self) -> Measurement2D:
        assert self.has_measurement()
        return Measurement2D.from_transformation(self.get_value())

    def set_measurement(self, measurement: Measurement2D) -> None:
        self.set_value(measurement.transformation())

    def draw_pose(self) -> SE3:
        return self.get_value().to_se3()

    def compute_ate2(self) -> float:
        assert self.has_truth()
        delta: Vector2 = self.get_truth().get_value().translation() - self.get_value().translation()
        return delta[0] ** 2 + delta[1] ** 2


class SpatialNodeFactory(object):
    _map: tp.Dict[Quantity, tp.Type[SubSpatialNode]] = {
        SE2: NodeSE2,
        Vector2: NodeV2
    }

    @classmethod
    def from_value_type(
            cls,
            value_type: tp.Type[Quantity]
    ) -> tp.Type[SubSpatialNode]:
        assert value_type in cls._map, f"Node with value type '{value_type}' not known."
        return cls._map[value_type]

    @classmethod
    def from_value(
            cls,
            value: Quantity,
            id_: tp.Optional[int] = None
    ) -> SubSpatialNode:
        node_type: tp.Type[SubSpatialNode] = cls.from_value_type(type(value))
        node: SubSpatialNode = node_type(id_=id_, value=value)
        return node
