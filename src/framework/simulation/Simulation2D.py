import typing as tp

from src.framework.graph.CalibratingGraph import SubCalibratingEdge, CalibratingGraph
from src.framework.graph.Graph import SubGraph, SubNode, SubEdge
from src.framework.graph.GraphManager import GraphManager
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.edges import EdgeFactory
from src.framework.graph.types.scslam2d.nodes.NodeFactory import NodeFactory
from src.framework.graph.types.scslam2d.nodes.NodeSE2 import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.simulation.sensors import SubSensor


class Simulation2D(object):

    # data
    _manager: GraphManager
    _sensors: tp.Dict[str, SubSensor]

    # poses
    _pose_ids: tp.List[int]
    _current: NodeSE2

    def __init__(self):
        self._manager = GraphManager(CalibratingGraph())
        self._sensors = {}

        self._pose_ids = []
        self._current = self.add_pose(SE2.from_translation_angle_elements(0, 0, 0))
        self._current.fix()

    # add elements
    def add_node(
            self,
            node: SubNode
    ) -> SubNode:
        """ Adds <node>. """

        self._manager.add_node(node)
        return node

    def add_node_from_value(
            self,
            value: Supported
    ) -> SubNode:
        """ Adds a new node with <value>. """

        node = NodeFactory.from_value(value)
        return self.add_node(node)

    def add_pose(
            self,
            pose: SE2
    ) -> NodeSE2:
        """ Adds a new pose-node (i.e., NodeSE2) with <value>. """

        node: NodeSE2 = self.add_node_from_value(pose)
        self._pose_ids.append(node.get_id())
        self._current = node
        return node

    def add_edge(
            self,
            edge: SubEdge
    ) -> SubEdge:
        """ Adds <edge>. """

        self._manager.add_edge(edge)
        return edge

    def add_edge_from_value(
            self,
            sensor_id: str,
            ids: tp.List[int],
            measurement: Supported
    ) -> SubEdge:
        """ Adds a new edge between <ids> with <measurement>, as measurement by <sensor_id>. """

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
        """ Adds a new pose and edge with <measurement>, as measured by <sensor_id>. """

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
    ) -> None:
        """ Adds a sensor with <sensor_id>. """

        sensor.set_graph(self._manager)
        self._sensors[id_] = sensor

    def has_sensor(
            self,
            sensor_id: str
    ) -> bool:
        """ Returns whether a sensor with <sensor_id> is added. """
        return sensor_id in self._sensors

    def get_sensor(
            self,
            sensor_id: str
    ) -> SubSensor:
        """ Returns the sensor with <sensor_id>. """

        assert self.has_sensor(sensor_id)
        return self._sensors[sensor_id]

    # nodes
    def get_node(self, id_: int) -> SubNode:
        """ Returns the node with <id_>. """
        return self._manager.get_graph().get_node(id_)

    def get_current(self) -> NodeSE2:
        """ Returns the current pose-node. """
        return self._current

    def get_current_pose(self) -> SE2:
        """ Returns the current pose. """
        return self._current.get_value()

    def get_current_id(self) -> int:
        """ Returns the id of the current pose-node. """
        return self._current.get_id()

    def get_pose_ids(self) -> tp.List[int]:
        """ Returns the pose-node id history. """
        return self._pose_ids

    # counter
    def get_count(self) -> int:
        """ Returns the counter-value of the GraphManager. """
        return self._manager.get_count()

    def set_counter(self, id_: int) -> None:
        """ Sets the counter-value of the GraphManager. """
        self._manager.set_count(id_)

    # graph
    def get_graph(self) -> SubGraph:
        """ Returns the graph. """
        return self._manager.get_graph()

    # timestamp
    def set_timestamp(self, timestamp: float) -> None:
        """ Sets the timestamp of the GraphManager. """
        self._manager.set_timestamp(timestamp)

    def increment_timestamp(self, delta: float) -> None:
        """ Increments the timestamp of the GraphManager by <delta>. """
        self._manager.increment_timestamp(delta)
