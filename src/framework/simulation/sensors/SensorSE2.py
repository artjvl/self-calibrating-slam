from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector3
from src.framework.simulation.sensors.Sensor import Sensor


class SensorSE2(Sensor[SE2]):

    _type = SE2

    def measure(self, value: SE2) -> SE2:
        # value = self.compose(value)
        noise: Vector3 = self.generate_noise()
        return value.oplus(noise)

    def compose(self, value: SE2) -> SE2:
        for parameter in self._parameters:
            value = parameter.compose_transformation(value)
        return value

    def decompose(self, value: SE2) -> SE2:
        for parameter in self._parameters[::-1]:
            value = parameter.compose_transformation(value, inverse=True)
        return value
