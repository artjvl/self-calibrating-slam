import copy
import typing as tp
from abc import abstractmethod

from src.framework.graph.CalibratingGraph import CalibratingGraph
from src.framework.graph.GraphManager import GraphManager
from src.framework.graph.GraphParser import GraphParser
from src.framework.graph.data.DataFactory import Quantity
from src.framework.graph.types.edges.EdgeFactory import EdgeFactory
from src.framework.graph.types.nodes.SpatialNode import NodeSE2, SpatialNodeFactory
from src.framework.math.lie.transformation import SE2
from src.framework.optimiser.Optimiser import Optimiser
from src.framework.simulation.Parameter import SlidingParameter

if tp.TYPE_CHECKING:
    from src.framework.graph.CalibratingGraph import SubCalibratingEdge, SubCalibratingGraph
    from src.framework.graph.Graph import SubGraph, SubNode, SubEdge
    from src.framework.simulation.Parameter import SubParameter
    from src.framework.simulation.Sensor import SubSensor

SubSimulation2D = tp.TypeVar('SubSimulation2D', bound='Simulation2D')


class Simulation2D(GraphManager):
    # sensors
    _sensors: tp.Dict[str, 'SubSensor']

    _optimiser: Optimiser
    _is_sliding: bool
    _has_closure: bool

    # poses
    _pose_ids: tp.List[int]
    _current: NodeSE2

    def __init__(self, optimiser: tp.Optional[Optimiser] = None):
        super().__init__(CalibratingGraph())
        self._sensors = {}

        if optimiser is None:
            optimiser = Optimiser()
        self._optimiser = optimiser
        self._is_sliding = False
        self._has_closure = False

        # poses
        self._pose_ids = []
        self._current = self.add_pose(SE2.from_translation_angle_elements(0, 0, 0))
        self._current.fix()

    # sensors
    def add_sensor(
            self,
            sensor_name: str,
            sensor: 'SubSensor'
    ) -> None:
        assert sensor_name not in self._sensors
        self._sensors[sensor_name] = sensor

    def has_sensor(self, sensor_name: str) -> bool:
        return sensor_name in self._sensors

    def get_sensor(
            self,
            sensor_name: str
    ) -> 'SubSensor':
        assert self.has_sensor(sensor_name), sensor_name
        return self._sensors[sensor_name]

    def get_sensor_names(self) -> tp.List[str]:
        return list(self._sensors.keys())

    def get_sensors(self) -> tp.List['SubSensor']:
        return list(self._sensors.values())

    # parameters
    def add_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            parameter: 'SubParameter'
    ) -> None:
        assert self.has_sensor(sensor_name), f'{sensor_name}'
        if isinstance(parameter, SlidingParameter):
            self._is_sliding = True
        self._sensors[sensor_name].add_parameter(parameter_name, parameter)
        self.add_node(parameter.get_node())

    def update_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity'
    ) -> None:
        sensor: 'SubSensor' = self.get_sensor(sensor_name)
        sensor.update_parameter(parameter_name, value)
        parameter: 'SubParameter' = sensor.get_parameter(parameter_name)
        self.add_node(parameter.get_node())

    # add elements
    def add_node_from_value(
            self,
            value: Quantity
    ) -> 'SubNode':
        """ Creates and adds a new node with <value>. """
        return self.add_node(SpatialNodeFactory.from_value(value))

    def add_pose(
            self,
            pose: SE2
    ) -> NodeSE2:
        """ Creates and adds a new pose-node (i.e., NodeSE2) with <value>. """

        node: NodeSE2 = self.add_node_from_value(pose)
        self._pose_ids.append(node.get_id())
        self._current = node
        return node

    def add_edge_from_value(
            self,
            sensor_name: str,
            ids: tp.List[int],
            measurement: Quantity,
            is_closure: bool = False
    ) -> 'SubEdge':
        """ Creates and adds a new edge between <ids> with <measurement>, as measurement by <sensor_name>. """
        sensor: 'SubSensor' = self.get_sensor(sensor_name)
        if is_closure:
            self._has_closure = True

        graph: 'SubGraph' = self.get_graph()
        nodes: tp.List['SubNode'] = [graph.get_node(id_) for id_ in ids]
        edge: 'SubCalibratingEdge' = EdgeFactory.from_measurement_nodes(
            measurement,
            nodes,
            name=sensor_name,
            info_matrix=sensor.get_info_matrix()
        )
        return self.add_edge(edge)

    def add_odometry(
            self,
            sensor_name: str,
            measurement: SE2
    ) -> tp.Tuple['SubNode', 'SubEdge']:
        """ Creates and adds a new pose and edge with <measurement>, as measured by <sensor_name>. """

        sensor: 'SubSensor' = self.get_sensor(sensor_name)
        transformation: SE2 = sensor.compose(measurement)

        current: NodeSE2 = self._current
        position: SE2 = current.get_value() + transformation
        new: NodeSE2 = self.add_pose(position)
        edge: 'SubCalibratingEdge' = self.add_edge_from_value(
            sensor_name,
            [current.get_id(), new.get_id()],
            measurement
        )
        for parameter in sensor.get_parameters():
            parameter.add_edge(edge)
        return new, edge

    # nodes
    def get_node(self, id_: int) -> 'SubNode':
        """ Returns the node with <id_>. """
        return self._graph.get_node(id_)

    def get_current(self) -> NodeSE2:
        """ Returns the current pose-node. """
        return self._current

    def get_pose_ids(self) -> tp.List[int]:
        """ Returns the pose-node id history. """
        return self._pose_ids

    @abstractmethod
    def step(self, delta: float) -> 'SubGraph':
        graph: 'SubCalibratingGraph' = self.get_graph()

        snapshot: 'SubCalibratingGraph'
        if self._is_sliding:
            if self._has_closure:
                # optimises the graph if a loop-closure was made
                solution = self._optimiser.instance_optimise(graph)
            else:
                solution = copy.deepcopy(graph)

            graph.from_vector(solution.to_vector())
            snapshot = copy.copy(solution)
        else:
            # creates a shallow-copy of the graph to be used as a previous
            snapshot = copy.copy(graph)
            graph.copy_meta_to(snapshot)
            if graph.has_previous():
                snapshot.set_previous(graph.get_previous())
        graph.set_previous(snapshot)

        self._has_closure = False
        self.increment_timestamp(delta)
        return snapshot
