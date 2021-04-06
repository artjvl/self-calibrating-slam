import typing as tp

from src.framework.math.matrix.square.Square import SubSquare, Square


class Square2(Square):
    _dim = 2


class Square3(Square):
    _dim = 3


class Square4(Square):
    _dim = 4


class SquareFactory(object):
    _map: tp.Dict[int, tp.Type[SubSquare]] = {
        2: Square2,
        3: Square3,
        4: Square4
    }

    @classmethod
    def from_dim(cls, dim: int) -> tp.Type[SubSquare]:
        return cls._map[dim]
