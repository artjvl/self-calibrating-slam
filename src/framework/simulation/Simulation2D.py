import typing as tp

from src.framework.graph.FactorGraph import SubFactorNode, SubFactorEdge
from src.framework.graph.Graph import SubGraph, Graph
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.scslam2d.edges import EdgeFactory
from src.framework.graph.types.scslam2d.edges.CalibratingEdge import SubCalibratingEdge
from src.framework.graph.types.scslam2d.nodes.topological import NodeSE2
from src.framework.graph.types.scslam2d.nodes.topological.NodeFactory import NodeFactory
from src.framework.math.lie.transformation import SE2
from src.framework.simulation.sensors import SubSensor


class Simulation2D(object):

    def __init__(self):
        self._graph: SubGraph = Graph()
        self._sensors: tp.Dict[str, SubSensor] = {}

        # starting position
        self._id_counter: int = 0
        self._par_counter: int = 10**9
        self._pose_ids: tp.List[int] = []
        self._current: NodeSE2 = self.add_pose(SE2.from_translation_angle_elements(0, 0, 0))
        self._current.fix()

    # add elements
    def add_node(
            self,
            node: SubFactorNode
    ) -> SubFactorNode:
        id_: int = self.count_id(increment=True)
        node.set_id(id_)
        self._graph.add_node(node)
        return node

    def add_node_from_value(
            self,
            value: Supported
    ) -> SubFactorNode:
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
            edge: SubFactorEdge
    ) -> SubFactorEdge:
        self._graph.add_edge(edge)
        return edge

    def add_edge_from_value(
            self,
            ids: tp.List[int],
            measurement: Supported,
            sensor_id: str
    ) -> SubGraph:
        nodes: tp.List[SubFactorNode] = [self._graph.get_node(id_) for id_ in ids]
        edge: SubCalibratingEdge = EdgeFactory.from_measurement_nodes(measurement, *nodes)

        sensor: SubSensor = self.get_sensor(sensor_id)
        edge = sensor.extend_edge(edge)
        return self.add_edge(edge)

    def add_odometry(
            self,
            measurement: SE2,
            sensor_id: str
    ) -> None:
        sensor: SubSensor = self.get_sensor(sensor_id)
        transformation: SE2 = sensor.compose(measurement)

        current: NodeSE2 = self.get_current()
        position: SE2 = current.get_value() + transformation
        new: NodeSE2 = self.add_pose(position)
        self.add_edge_from_value([current.get_id(), new.get_id()], measurement, sensor_id)

    # sensors
    def add_sensor(
            self,
            id_: str,
            sensor: SubSensor
    ):
        sensor.set_simulation(self)
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
    def count_id(self, increment: bool = False) -> int:
        if increment:
            self._id_counter += 1
        return self._id_counter

    def get_node(self, id_: int) -> SubFactorNode:
        return self._graph.get_node(id_)

    def get_current(self) -> NodeSE2:
        return self._current

    def get_current_pose(self) -> SE2:
        return self._current.get_value()

    def get_current_id(self) -> int:
        return self._current.get_id()

    def set_current_id(self, id_: int) -> None:
        assert id_ >= self.get_current_id()
        self._id_counter = id_

    def get_pose_ids(self) -> tp.List[int]:
        """ Returns the pose-id history. """
        return self._pose_ids

    def get_graph(self) -> SubGraph:
        return self._graph
