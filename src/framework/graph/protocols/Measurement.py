import typing as tp

from src.framework.math.lie.rotation import SO2
from src.framework.math.lie.rotation import SOFactory
from src.framework.math.lie.transformation import SE2
from src.framework.math.lie.transformation import SEFactory
from src.framework.math.matrix.vector import Vector2, Vector3
from src.framework.math.matrix.vector import VectorFactory

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
            transformation: tp.Optional['SubSE'] = None,
            translation: tp.Optional['SubSizeVector'] = None,
            rotation: tp.Optional['SubSO'] = None
    ):
        self._transformation = None
        self._translation = None
        self._rotation = None

        if transformation is not None:
            self.set_transformation(transformation)
        else:
            if translation is not None:
                self.set_translation(translation)
            if rotation is not None:
                self.set_rotation(rotation)

    # transformation
    def set_transformation(self, transformation: 'SubSE') -> None:
        self.set_translation(transformation.translation())
        self.set_rotation(transformation.rotation())
        self._transformation = transformation

    def has_transformation(self) -> bool:
        return self._transformation is not None

    def transformation(self) -> 'SubSE':
        if self.has_transformation():
            return self._transformation
        return SEFactory.from_dim(self._dim)(self.translation(), self.rotation())

    # translation
    def set_translation(self, translation: 'SubSizeVector') -> None:
        self._translation = translation
        if self.has_rotation():
            self._transformation = SEFactory.from_dim(self._dim)(translation, self.rotation())

    def has_translation(self) -> bool:
        return self._translation is not None

    def translation(self) -> 'SubSizeVector':
        if self.has_translation():
            return self._translation
        return VectorFactory.from_dim(self._dim).zeros()

    # rotation
    def set_rotation(self, rotation: SO2) -> None:
        self._rotation = rotation
        if self.has_translation():
            self._transformation = SEFactory.from_dim(self._dim)(self.translation(), rotation)

    def has_rotation(self) -> bool:
        return self._rotation is not None

    def rotation(self) -> SO2:
        if self.has_rotation():
            return self._rotation
        return SOFactory.from_dim(self._dim).from_zeros()

    # type
    def get_type(self) -> tp.Type[tp.Any]:
        if self.has_transformation():
            return SEFactory.from_dim(self._dim)
        if self.has_translation():
            return VectorFactory.from_dim(self._dim)
        return SOFactory.from_dim(self._dim)

    def vector(self) -> 'SubSizeVector':
        return self.transformation().vector()

    # mask
    def mask(self, transformation: 'SubSE') -> None:
        if self.has_translation():
            self.set_translation(transformation.translation())
        if self.has_rotation():
            self.set_rotation(transformation.rotation())

    # alternative constructors
    @classmethod
    def from_translation(cls, translation: 'SubSizeVector') -> SubMeasurement:
        return cls(translation=translation)

    @classmethod
    def from_rotation(cls, rotation: 'SubSO') -> SubMeasurement:
        return cls(rotation=rotation)

    @classmethod
    def from_transformation(cls, transformation: 'SubSE') -> SubMeasurement:
        return cls(transformation=transformation)


class Measurement2D(Measurement):
    _dim = 2

    _translation: tp.Optional[Vector2]
    _rotation: tp.Optional[SO2]
    _transformation: tp.Optional[SE2]

    # rotation
    def set_angle(self, angle: float) -> None:
        self.set_rotation(SO2.from_angle(angle))

    def angle(self) -> float:
        if self.has_rotation():
            return self._rotation.angle()
        return 0.

    def vector(self) -> Vector3:
        transformation: SE2 = self.transformation()
        return transformation.translation_angle_vector()

    # alternative constructors
    @classmethod
    def from_angle(cls, angle: float) -> 'Measurement2D':
        rotation: tp.Optional[SO2] = None
        if angle is not None:
            rotation = SO2.from_angle(angle)
        return cls(rotation=rotation)
