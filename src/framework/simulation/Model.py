import typing as tp


if tp.TYPE_CHECKING:
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.Graph import SubParameterNode
    from src.framework.simulation.Parameter import SubParameter
    from src.framework.simulation.Sensor import SubSensor

SubModel = tp.TypeVar('SubModel', bound='Model')


class Model(object):
    _sensors: tp.Dict[str, 'SubSensor']

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._sensors = {}

    def has_sensor(self, sensor_name: str) -> bool:
        """ Returns whether a sensor is present. """
        return sensor_name in self._sensors

    def add_sensor(
            self,
            sensor_name: str,
            sensor: 'SubSensor'
    ) -> None:
        """ Adds a sensor. """
        assert sensor_name not in self._sensors
        self._sensors[sensor_name] = sensor

    def get_sensor(
            self,
            sensor_name: str
    ) -> 'SubSensor':
        """ Returns a sensor. """
        assert self.has_sensor(sensor_name), sensor_name
        return self._sensors[sensor_name]

    def get_sensor_names(self) -> tp.List[str]:
        """ Returns all sensor names. """
        return list(self._sensors.keys())

    def get_sensors(self) -> tp.List['SubSensor']:
        """ Returns all sensors. """
        return list(self._sensors.values())

    def add_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            parameter: 'SubParameter'
    ) -> 'SubParameterNode':
        return self.get_sensor(sensor_name).add_parameter(parameter_name, parameter)

    def update_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity'
    ) -> 'SubParameterNode':
        return self.get_sensor(sensor_name).update_parameter(parameter_name, value)
