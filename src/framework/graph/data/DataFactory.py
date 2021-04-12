import typing as tp

from src.framework.graph.data.Data import SubData
from src.framework.graph.data.DataSE import DataSE2
from src.framework.graph.data.DataSquare import DataSquare2, DataSquare3
from src.framework.graph.data.DataVector import DataV2, DataV3, DataV6
from src.framework.math.lie.transformation import SE2
from src.framework.math.lie.transformation.SE import SubSE
from src.framework.math.matrix.square import SubSquare, Square2, Square3
from src.framework.math.matrix.vector import Vector2, Vector3, Vector6, SubVector

Supported = tp.Union[SubSE, SubVector, SubSquare]


class DataFactory(object):
    """ A helper-class for creating Data-objects. """

    _map: tp.Dict[tp.Type[Supported], tp.Type[SubData]] = {
        SE2: DataSE2,
        Vector2: DataV2,
        Vector3: DataV3,
        Vector6: DataV6,
        Square2: DataSquare2,
        Square3: DataSquare3
    }

    @classmethod
    def from_type(cls, type_: tp.Type[Supported]) -> tp.Type[SubData]:
        """ Returns the corresponding data-object for a given value-type. """
        assert type_ in cls._map, f'Type {type_} not supported.'
        return cls._map[type_]

    @classmethod
    def from_value(cls, value: Supported) -> SubData:
        """ Returns the corresponding data-object for a given value. """
        return cls.from_type(type(value))(value)
