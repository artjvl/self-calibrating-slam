import typing as tp

from src.framework.math.lie.transformation.SE import SubSE
from src.framework.math.lie.transformation.SE2 import SE2
from src.framework.math.lie.transformation.SE3 import SE3


class SEFactory(object):
    _map: tp.Dict[int, tp.Type[SubSE]] = {
        2: SE2,
        3: SE3
    }

    @classmethod
    def from_dim(cls, dim: int) -> tp.Type[SubSE]:
        return cls._map[dim]
