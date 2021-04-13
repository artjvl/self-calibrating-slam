import typing as tp

from src.framework.graph.FactorGraph import SubNode
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.CalibratingGraph import CalibratingGraph, SubCalibratingGraph
from src.framework.graph.types.scslam2d.edges import EdgeFactory
from src.framework.graph.types.scslam2d.edges.CalibratingEdge import SubCalibratingEdge
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import SubCalibratingNode
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import SubInformationNode
from src.framework.graph.types.scslam2d.nodes.parameter.ParameterNode import SubParameterNode
from src.framework.graph.types.scslam2d.nodes.typological import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.simulation.sensors.Sensor import SubSensor


class Simulation2D(object):

    def __init__(self):  # :^)
        self._graph: SubCalibratingGraph = CalibratingGraph()
        self._sensors: tp.Dict[str, SubSensor] = {}

        # starting position
        self._id_counter: int = 0
        self._pose_ids: tp.List[int] = []
        self._current: NodeSE2 = self.add_pose(SE2.from_translation_angle_elements(0, 0, 0))
        self._current.fix()

    # sensors
    def add_sensor(
            self,
            id_: str,
            sensor: SubSensor
    ):
        parameter: SubParameterNode
        for parameter in sensor.get_parameters():
            parameter.set_id(self.get_id(increment=True))
            self._graph.add_node(parameter)

        if sensor.has_info_node():
            information: SubInformationNode = sensor.get_info_node()
            information.set_id(self.get_id(increment=True))
            self._graph.add_node(information)

        self._sensors[id_] = sensor

    def has_sensor(
            self,
            sensor_id: str
    ) -> bool:
        return sensor_id in self._sensors

    def get_sensor(
            self,
            sensor_id: str
    ) -> SubSensor:
        assert self.has_sensor(sensor_id)
        return self._sensors[sensor_id]

    # odometry
    def add_odometry(
            self,
            transformation: SE2,
            sensor_id: str
    ) -> None:
        # current node
        current: NodeSE2 = self.get_current()

        # next node
        position: SE2 = current.get_value() + transformation
        new = self.add_pose(position)

        # edge
        self.add_edge([current.get_id(), new.get_id()], transformation, sensor_id)

    # edges
    def add_edge(
            self,
            ids: tp.List[int],
            value: Supported,
            sensor_id: str
    ) -> SubCalibratingEdge:
        nodes: tp.List[SubCalibratingNode] = [self._graph.get_node(id_) for id_ in ids]
        edge: SubCalibratingEdge = EdgeFactory.from_measurement_nodes(value, *nodes)

        assert self.has_sensor(sensor_id)
        sensor: SubSensor = self.get_sensor(sensor_id)
        edge = sensor.compose_edge(edge, value)
        self._graph.add_edge(edge)
        return edge

    # poses
    def add_pose(
            self,
            pose: SE2
    ) -> NodeSE2:
        id_: int = self.get_id(increment=True)
        node = NodeSE2(id_, pose)
        self._pose_ids.append(id_)
        self._graph.add_node(node)
        self._current = node
        return node

    def get_node(self, id_: int) -> SubNode:
        return self._graph.get_node(id_)

    def get_current(self) -> NodeSE2:
        return self._current

    def get_current_pose(self) -> SE2:
        return self._current.get_value()

    def get_current_id(self) -> int:
        return self._current.get_id()

    def get_pose_ids(self) -> tp.List[int]:
        return self._pose_ids

    def get_id(self, increment: bool = False) -> int:
        if increment:
            self._id_counter += 1
        return self._id_counter

    def get_graph(self) -> SubCalibratingGraph:
        return self._graph
