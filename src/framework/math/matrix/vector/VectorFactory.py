import typing as tp

from src.framework.math.matrix.vector.Vector import SizeVector, SubVector


class Vector1(SizeVector):
    _dim = 1

    def x(self) -> float:
        return self[0]


class Vector2(SizeVector):
    _dim = 2

    def x(self) -> float:
        return self[0]

    def y(self) -> float:
        return self[1]

    def to_vector3(self) -> 'Vector3':
        return Vector3(*(self.to_list()), 0)


class Vector3(SizeVector):
    _dim = 3

    def x(self) -> float:
        return self[0]

    def y(self) -> float:
        return self[1]

    def z(self) -> float:
        return self[2]

    def split(self) -> tp.Tuple[Vector2, float]:
        return Vector2(self[:2]), self[2]


class Vector4(SizeVector):
    _dim = 4

    def x(self) -> float:
        return self[0]

    def y(self) -> float:
        return self[1]

    def z(self) -> float:
        return self[2]

    def w(self) -> float:
        return self[3]


class Vector6(SizeVector):
    _dim = 6

    def x(self) -> float:
        return self[0]

    def y(self) -> float:
        return self[1]

    def z(self) -> float:
        return self[2]

    def a(self) -> float:
        return self[3]

    def b(self) -> float:
        return self[4]

    def c(self) -> float:
        return self[5]

    def split(self) -> tp.Tuple[Vector3, Vector3]:
        return Vector3(self[:3]), Vector3(self[3:])


class VectorFactory(object):
    _map: tp.Dict[int, tp.Type[SubVector]] = {
        1: Vector1,
        2: Vector2,
        3: Vector3,
        4: Vector4,
        6: Vector6
    }

    @classmethod
    def from_dim(cls, dim: int) -> tp.Type[SubVector]:
        assert dim in cls._map
        return cls._map[dim]

    @classmethod
    def from_list(cls, list_: tp.List[float]) -> SubVector:
        assert len(list_) in cls._map
        return cls._map[len(list_)](list_)
