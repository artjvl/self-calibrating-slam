import typing as tp

from src.framework.math.lie.rotation import SO2, SOFactory
from src.framework.math.lie.rotation.SO import SO
from src.framework.math.lie.transformation import SE2, SEFactory
from src.framework.math.lie.transformation.SE import SE
from src.framework.math.matrix.vector import Vector2, Vector3, VectorFactory
from src.framework.math.matrix.vector.Vector import SizeVector

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.vector.Vector import SubSizeVector
    from src.framework.math.lie.transformation.SE import SubSE
    from src.framework.math.lie.rotation.SO import SubSO

SubMeasurement = tp.TypeVar('SubMeasurement', bound='Measurement')


class Measurement(object):
    _dim: int

    _transformation: tp.Optional['SubSE']
    _translation: tp.Optional['SubSizeVector']
    _rotation: tp.Optional['SubSO']

    def __init__(
            self,
            value: tp.Union['SubSE', 'SubSO', 'SubSizeVector']
    ):
        assert isinstance(value, (SE, SO, SizeVector))
        if isinstance(value, SE):
            self.set_transformation(value)
        elif isinstance(value, SO):
            self.set_rotation(value)
        else:
            self.set_translation(value)

    # transformation
    def set_transformation(self, transformation: 'SubSE') -> None:
        self.set_translation(transformation.translation())
        self.set_rotation(transformation.rotation())
        self._transformation = transformation

    def has_transformation(self) -> bool:
        return self._transformation is not None

    def get_transformation(self) -> 'SubSE':
        if self.has_transformation():
            return self._transformation
        return SEFactory.from_dim(self._dim)(self.get_translation(), self.get_rotation())

    # translation
    def set_translation(self, translation: 'SubSizeVector') -> None:
        self._translation = translation
        if self.has_rotation():
            self._transformation = SEFactory.from_dim(self._dim)(translation, self.get_rotation())

    def has_translation(self) -> bool:
        return self._translation is not None

    def get_translation(self) -> 'SubSizeVector':
        if self.has_translation():
            return self._translation
        return VectorFactory.from_dim(self._dim).zeros()

    # rotation
    def set_rotation(self, rotation: 'SubSO') -> None:
        self._rotation = rotation
        if self.has_translation():
            self._transformation = SEFactory.from_dim(self._dim)(self.get_translation(), rotation)

    def has_rotation(self) -> bool:
        return self._rotation is not None

    def get_rotation(self) -> SO2:
        if self.has_rotation():
            return self._rotation
        return SOFactory.from_dim(self._dim).from_zeros()

    def vector(self) -> 'SubSizeVector':
        return self.get_transformation().vector()

    # mask
    def mask(self, transformation: 'SubSE') -> None:
        if self.has_translation():
            self.set_translation(transformation.translation())
        if self.has_rotation():
            self.set_rotation(transformation.rotation())


class MeasurementSE2(Measurement):
    _dim = 2

    _translation: tp.Optional[Vector2]
    _rotation: tp.Optional[SO2]
    _transformation: tp.Optional[SE2]

    def __init__(
            self,
            value: tp.Union[SE2, SO2, float, Vector2]
    ):
        if isinstance(value, float):
            value = SO2.from_angle(value)
        super().__init__(value)

    # rotation
    def set_angle(self, angle: float) -> None:
        self.set_rotation(SO2.from_angle(angle))

    def get_angle(self) -> float:
        if self.has_rotation():
            return self._rotation.angle()
        return 0.

    def vector(self) -> Vector3:
        return self.get_transformation().translation_angle_vector()
