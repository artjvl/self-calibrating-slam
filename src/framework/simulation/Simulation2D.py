import typing as tp

from src.framework.graph.Graph import SubGraph, Graph, SubNode, SubEdge
from src.framework.graph.GraphManager import GraphManager
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.edges import EdgeFactory
from src.framework.graph.types.scslam2d.edges.CalibratingEdge import SubCalibratingEdge
from src.framework.graph.types.scslam2d.nodes.NodeFactory import NodeFactory
from src.framework.graph.types.scslam2d.nodes.NodeSE2 import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.simulation.sensors import SubSensor


class Simulation2D(object):

    _manager: GraphManager
    _sensors: tp.Dict[str, SubSensor]

    _pose_ids: tp.List[int]
    _current: NodeSE2

    def __init__(self):
        self._manager = GraphManager(Graph())
        self._sensors = {}

        self._pose_ids = []
        self._current = self.add_pose(SE2.from_translation_angle_elements(0, 0, 0))
        self._current.fix()

    # add elements
    def add_node(
            self,
            node: SubNode
    ) -> SubNode:
        self._manager.add_node(node)
        return node

    def add_node_from_value(
            self,
            value: Supported
    ) -> SubNode:
        node = NodeFactory.from_value(value)
        return self.add_node(node)

    def add_pose(
            self,
            pose: SE2
    ) -> NodeSE2:
        node: NodeSE2 = self.add_node_from_value(pose)
        self._pose_ids.append(node.get_id())
        self._current = node
        return node

    def add_edge(
            self,
            edge: SubEdge
    ) -> SubEdge:
        self._manager.add_edge(edge)
        return edge

    def add_edge_from_value(
            self,
            sensor_id: str,
            ids: tp.List[int],
            measurement: Supported
    ) -> SubEdge:
        graph: SubGraph = self._manager.get_graph()
        nodes: tp.List[SubNode] = [graph.get_node(id_) for id_ in ids]
        edge: SubCalibratingEdge = EdgeFactory.from_measurement_nodes(measurement, *nodes)

        sensor: SubSensor = self.get_sensor(sensor_id)
        edge = sensor.extend_edge(edge)
        return self.add_edge(edge)

    def add_odometry(
            self,
            sensor_id: str,
            measurement: SE2
    ) -> SubEdge:
        sensor: SubSensor = self.get_sensor(sensor_id)
        transformation: SE2 = sensor.compose(measurement)

        current: NodeSE2 = self._current
        position: SE2 = current.get_value() + transformation
        new: NodeSE2 = self.add_pose(position)
        return self.add_edge_from_value(
            sensor_id,
            [current.get_id(), new.get_id()],
            measurement
        )

    # sensors
    def add_sensor(
            self,
            id_: str,
            sensor: SubSensor
    ):
        sensor.set_graph(self._manager)
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

    # getters
    def get_node(self, id_: int) -> SubNode:
        return self._manager.get_graph().get_node(id_)

    def get_current(self) -> NodeSE2:
        return self._current

    def get_current_pose(self) -> SE2:
        return self._current.get_value()

    def get_current_id(self) -> int:
        return self._current.get_id()

    def get_count(self) -> int:
        return self._manager.get_count()

    def set_counter(self, id_: int) -> None:
        self._manager.set_count(id_)

    def get_pose_ids(self) -> tp.List[int]:
        """ Returns the pose-id history. """
        return self._pose_ids

    def get_graph(self) -> SubGraph:
        return self._manager.get_graph()
