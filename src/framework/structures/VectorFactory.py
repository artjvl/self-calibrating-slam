import typing as tp

from src.framework.structures import Vector2, Vector3
from src.framework.structures.Vector import SubVector, Vector


class VectorFactory(object):
    _map: tp.Dict[int, tp.Type[SubVector]] = {
        2: Vector2,
        3: Vector3
    }

    @classmethod
    def from_dim(cls, dim: int) -> tp.Type[SubVector]:
        if dim in cls._map:
            return cls._map[dim]
        return Vector
