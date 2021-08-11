import typing as tp

from src.framework.math.lie.rotation import SO2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2, Vector1, Vector3

SubMeasurement2D = tp.TypeVar('SubMeasurement2D', bound='Measurement2D')


class Measurement2D(object):
    _translation: tp.Optional[Vector2]
    _rotation: tp.Optional[SO2]
    _transformation: tp.Optional[SE2]

    def __init__(
            self,
            transformation: tp.Optional[SE2] = None,
            translation: tp.Optional[Vector2] = None,
            angle: tp.Optional[float] = None
    ):
        self._translation = None
        self._rotation = None
        self._transformation = None

        if transformation is not None:
            self.set_transformation(transformation)
        else:
            if translation is not None:
                self.set_translation(translation)
            if angle is not None:
                self.set_angle(angle)

    # translation
    def set_translation(self, translation: Vector2) -> None:
        self._translation = translation
        if self.has_rotation():
            self._transformation = SE2(translation, self.rotation())

    def has_translation(self) -> bool:
        return self._translation is not None

    def translation(self) -> Vector2:
        if self.has_translation():
            return self._translation
        return Vector2.zeros()

    # rotation
    def set_rotation(self, rotation: SO2) -> None:
        self._rotation = rotation
        if self.has_translation():
            self._transformation = SE2(self.translation(), rotation)

    def set_angle(self, angle: float) -> None:
        self.set_rotation(SO2.from_angle(angle))

    def has_rotation(self) -> bool:
        return self._rotation is not None

    def rotation(self) -> SO2:
        if self.has_rotation():
            return self._rotation
        return SO2.from_angle(0.)

    def angle(self) -> float:
        if self.has_rotation():
            return self._rotation.angle()
        return 0.

    # transformation
    def set_transformation(self, transformation: SE2) -> None:
        self.set_translation(transformation.translation())
        self.set_rotation(transformation.rotation())
        self._transformation = transformation

    def has_transformation(self) -> bool:
        return self._transformation is not None

    def transformation(self) -> SE2:
        if self.has_transformation():
            return self._transformation
        return SE2(self.translation(), self.rotation())

    # type
    def get_type(self) -> tp.Type[tp.Any]:
        if self.has_transformation():
            return SE2
        if self.has_translation():
            return Vector2
        return Vector1

    def get_dim(self) -> int:
        return 2 * int(self.has_translation()) + int(self.has_rotation())

    def vector(self) -> Vector3:
        translation = self.translation()
        return Vector3(translation[0], translation[1], self.angle())

    # mask
    def mask(self, transformation: SE2) -> None:
        if self.has_translation():
            self.set_translation(transformation.translation())
        if self.has_rotation():
            self.set_rotation(transformation.rotation())

    # alternative constructors
    @classmethod
    def from_translation(cls, translation: Vector2) -> SubMeasurement2D:
        return cls(translation=translation)

    @classmethod
    def from_angle(cls, angle: float) -> SubMeasurement2D:
        return cls(angle=angle)

    @classmethod
    def from_transformation(cls, transformation: SE2) -> SubMeasurement2D:
        return cls(transformation=transformation)
