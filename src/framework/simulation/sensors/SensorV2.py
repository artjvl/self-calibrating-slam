from src.framework.math.matrix.vector import Vector2
from src.framework.simulation.sensors.Sensor import Sensor


class SensorV2(Sensor[Vector2]):

    _type = Vector2

    def measure(self, value: Vector2) -> Vector2:
        for parameter in self._parameters:
            value = parameter.compose_translation(value, inverse=True)

        noise: Vector2 = self.generate_noise()
        return Vector2(value.array() + noise.array())

    def compose(self, value: Vector2) -> Vector2:
        for parameter in self._parameters:
            value = parameter.compose_translation(value)
        return value

    def decompose(self, value: Vector2) -> Vector2:
        for parameter in self._parameters[::-1]:
            value = parameter.compose_translation(value, inverse=True)
        return value
