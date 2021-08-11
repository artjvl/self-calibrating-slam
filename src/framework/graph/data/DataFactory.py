import typing as tp

from src.framework.graph.data.Data import SubData
from src.framework.graph.data.DataSE import DataSE2
from src.framework.graph.data.DataSymmetric import DataSymmetric2, DataSymmetric3
from src.framework.graph.data.DataVector import DataV1, DataV2, DataV3, DataV6
from src.framework.math.lie.transformation import SE2
from src.framework.math.lie.transformation.SE import SubSE
from src.framework.math.matrix.Matrix import SubMatrix
from src.framework.math.matrix.square import Square2, Square3
from src.framework.math.matrix.vector import Vector1, Vector2, Vector3, Vector6, SubVector

Value = tp.Union[SubSE, SubVector]
Quantity = tp.Union[Value, SubMatrix]


class DataFactory(object):
    """ A helper-class for creating Data-objects. """

    _map: tp.Dict[tp.Type[Quantity], tp.Type[SubData]] = {
        SE2: DataSE2,
        Vector1: DataV1,
        Vector2: DataV2,
        Vector3: DataV3,
        Vector6: DataV6,
        Square2: DataSymmetric2,
        Square3: DataSymmetric3
    }

    @classmethod
    def from_type(cls, type_: tp.Type[Quantity]) -> tp.Type[SubData]:
        """ Returns the corresponding data-object for a given value-type. """
        assert type_ in cls._map, f'Type {type_} not supported.'
        return cls._map[type_]

    @classmethod
    def from_value(cls, value: Quantity) -> SubData:
        """ Returns the corresponding data-object for a given value. """
        return cls.from_type(type(value))(value)
