import copy
import typing as tp
from abc import abstractmethod, ABC

from src.framework.graph.CalibratingGraph import CalibratingGraph
from src.framework.graph.GraphManager import GraphManager
from src.framework.graph.types.edges.EdgeFactory import EdgeFactory
from src.framework.graph.types.nodes.SpatialNode import NodeSE2, SpatialNodeFactory
from src.framework.math.lie.transformation import SE2
from src.framework.optimiser.Optimiser import Optimiser

if tp.TYPE_CHECKING:
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.CalibratingGraph import SubCalibratingEdge, SubCalibratingGraph
    from src.framework.graph.Graph import SubGraph, SubNode, SubEdge
    from src.framework.simulation.Parameter import SubParameter
    from src.framework.simulation.PostAnalyser import SubPostAnalyser
    from src.framework.simulation.Sensor import SubSensor

SubSubSimulation2D = tp.TypeVar('SubSubSimulation2D', bound='Simulation2D')


class SubModel2D(GraphManager):
    _sensors: tp.Dict[str, 'SubSensor']  # sensors
    _optimiser: Optimiser  # optimiser

    _pose_ids: tp.List[int]  # list of pose-ids
    _current_node: NodeSE2  # current pose-node
    _last_graph: 'SubGraph'  # last saved instance of the graph

    def __init__(self, optimiser: tp.Optional[Optimiser] = None):
        super().__init__()
        if optimiser is None:
            optimiser = Optimiser()
        self._optimiser = optimiser
        self._sensors = {}
        self.reset()

    def reset(self) -> None:
        super().reset()

        self._pose_ids = []
        self._current_node = self.add_pose(SE2.from_translation_angle_elements(0, 0, 0))
        self._current_node.fix()
        self._last_graph = super().graph()

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
            value: 'Quantity'
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
        self._current_node = node
        return node

    def add_edge_from_value(
            self,
            sensor_name: str,
            ids: tp.List[int],
            measurement: 'Quantity'
    ) -> 'SubEdge':
        """ Creates and adds a new edge between <ids> with <measurement>, as measurement by <sensor_name>. """
        sensor: 'SubSensor' = self.get_sensor(sensor_name)
        graph: 'SubGraph' = self.graph()

        # create edge
        nodes: tp.List['SubNode'] = [graph.get_node(id_) for id_ in ids]
        edge: 'SubCalibratingEdge' = EdgeFactory.from_measurement_nodes(
            measurement,
            nodes,
            name=sensor_name,
            info_matrix=sensor.get_info_matrix()
        )

        # add parameter(s) to edge
        for parameter in sensor.get_parameters():
            parameter.add_edge(edge)

        # add edge to graph
        return self.add_edge(edge)

    def add_odometry(
            self,
            sensor_name: str,
            measurement: SE2
    ) -> tp.Tuple['SubNode', 'SubEdge']:
        """ Creates and adds a new pose and edge with <measurement>, as measured by <sensor_name>. """

        sensor: 'SubSensor' = self.get_sensor(sensor_name)
        transformation: SE2 = sensor.compose(measurement)

        current: NodeSE2 = self._current_node
        position: SE2 = current.get_value() + transformation
        new: NodeSE2 = self.add_pose(position)
        edge: 'SubCalibratingEdge' = self.add_edge_from_value(
            sensor_name,
            [current.get_id(), new.get_id()],
            measurement
        )
        return new, edge

    def report_closure(self) -> None:
        pass

    # nodes
    def get_node(self, id_: int) -> 'SubNode':
        """ Returns the node with <id_>. """
        return self._graph.get_node(id_)

    def get_current(self) -> NodeSE2:
        """ Returns the current pose-node. """
        return self._current_node

    def get_pose_ids(self) -> tp.List[int]:
        """ Returns the pose-node id history. """
        return self._pose_ids

    @abstractmethod
    def step(self, delta: float) -> 'SubGraph':
        pass

    # optimiser
    def set_optimiser(self, optimiser: Optimiser) -> None:
        self._optimiser = optimiser

    def has_optimiser(self) -> bool:
        return self._optimiser is not None

    def get_optimiser(self) -> Optimiser:
        assert self.has_optimiser()
        return self._optimiser

    def optimise(self) -> 'SubGraph':
        graph: 'SubCalibratingGraph' = self.graph()
        solution: 'SubCalibratingGraph' = self.get_optimiser().instance_optimise(graph)
        graph.copy_meta_to(solution)
        if graph.has_previous():
            solution.set_previous(graph.get_previous())
        graph.from_vector(solution.to_vector())
        return solution

    def copy(self, copy_: 'SubGraph') -> 'SubCalibratingGraph':
        graph: 'SubCalibratingGraph' = self.graph()
        graph.copy_meta_to(copy_)
        if graph.has_previous():
            copy_.set_previous(graph.get_previous())
        return copy_

    def set_previous(self, previous: 'SubGraph') -> None:
        graph: 'SubGraph' = self.graph()
        graph.set_previous(previous)
        self._last_graph = previous


class PlainSubModel2D(SubModel2D):

    def __init__(self, optimiser: tp.Optional[Optimiser] = None):
        super().__init__(optimiser=optimiser)
        self.set_timestamp()

    def step(self, delta: float) -> 'SubGraph':
        snapshot: 'SubCalibratingGraph' = self.copy(copy.copy(self.graph()))
        self.set_previous(snapshot)

        self.increment_timestamp(delta)
        return snapshot


class OptimisingSubModel2D(SubModel2D, ABC):
    _is_closure: bool  # indicates whether a closure has occurred at this step

    def __init__(self, optimiser: tp.Optional[Optimiser] = None):
        super().__init__(optimiser=optimiser)
        self._is_closure = False
        self.set_timestamp()

    def add_odometry(
            self,
            sensor_name: str,
            measurement: SE2
    ) -> tp.Tuple['SubNode', 'SubEdge']:
        self._is_closure = False
        return super().add_odometry(sensor_name, measurement)

    def report_closure(self) -> None:
        self._is_closure = True
        for sensor in self.get_sensors():
            for parameter in sensor.get_parameters():
                parameter.receive_closure()


class IncrementalSubModel2D(OptimisingSubModel2D):

    def step(self, delta: float) -> 'SubGraph':
        solution: 'SubGraph'
        if self._is_closure:
            solution = self.optimise()
        else:
            solution = self.copy(copy.copy(self.graph()))
        self.set_previous(solution)

        self.increment_timestamp(delta)
        return solution


class SlidingSubModel2D(OptimisingSubModel2D):

    def step(self, delta: float) -> 'SubGraph':
        solution: 'SubGraph'
        if self._is_closure:
            solution = self.optimise()
        else:
            solution = self.copy(copy.deepcopy(self.graph()))
        self.set_previous(solution)

        self.increment_timestamp(delta)
        return solution


class PostSubModel2D(OptimisingSubModel2D):
    _analyser: tp.Optional['SubPostAnalyser']
    _sensor_name: tp.Optional[str]

    def __init__(self, optimiser: tp.Optional[Optimiser] = None):
        super().__init__(optimiser=optimiser)
        self._analyser = None
        self._sensor_name = None

    def has_analyser(self) -> bool:
        return self._analyser is not None

    def get_analyser(self) -> 'SubPostAnalyser':
        return self._analyser

    def add_analyser(
            self,
            sensor_name: str,
            analyser: 'SubPostAnalyser'
    ) -> None:
        self._analyser = analyser
        self._sensor_name = sensor_name

    def add_edge_from_value(
            self,
            sensor_name: str,
            ids: tp.List[int],
            measurement: 'Quantity'
    ) -> 'SubEdge':
        edge: 'SubEdge' = super().add_edge_from_value(sensor_name, ids, measurement)
        if sensor_name == self._sensor_name:
            self._analyser.add_edge(edge)
        return edge

    def step(self, delta: float) -> 'SubGraph':
        pass

    def post_process(
            self,
            steps: int = 1
    ) -> None:
        assert self.has_analyser()
        analyser: SubPostAnalyser = self.get_analyser()

        previous: 'SubGraph' = self.optimise()
        for _ in range(steps):
            self.set_previous(previous)
            analyser.post_process()
            previous = self.optimise()
