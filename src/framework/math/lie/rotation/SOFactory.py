import typing as tp

from src.framework.math.lie.rotation.SO import SubSO
from src.framework.math.lie.rotation.SO2 import SO2
from src.framework.math.lie.rotation.SO3 import SO3


class SOFactory(object):
    _map: tp.Dict[int, tp.Type[SubSO]] = {
        2: SO2,
        3: SO3
    }

    @classmethod
    def from_dim(cls, dim: int) -> tp.Type[SubSO]:
        return cls._map[dim]
