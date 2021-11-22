import typing as tp
from abc import abstractmethod, ABC

from src.framework.graph.GraphManager import GraphManager
from src.framework.graph.constraint.EdgeFactory import EdgeFactory
from src.framework.graph.spatial.SpatialNodeFactory import SpatialNodeFactory
from src.framework.math.lie.transformation import SE2
from src.framework.optimiser.Optimiser import Optimiser
from src.framework.simulation.Model import Model
from src.framework.simulation.Parameter import StaticParameter, TimelyBatchParameter, SlidingParameter, \
    OldSlidingParameter
from src.framework.simulation.PostAnalyser import SpatialBatchAnalyser

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubNode, SubParameterNode, SubEdge, SubGraph
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification
    from src.framework.graph.spatial.NodeSE2 import NodeSE2
    from src.framework.simulation.Model import SubModel
    from src.framework.simulation.Parameter import SubParameter
    from src.framework.simulation.PostAnalyser import SubPostAnalyser
    from src.framework.simulation.Sensor import SubSensor


SubSimulation = tp.TypeVar('SubSimulation', bound='Simulation')


class Simulation(GraphManager):
    _model: 'SubModel'
    _optimiser: Optimiser

    _pose_ids: tp.List[int]  # list of pose-ids
    _current_node: 'NodeSE2'  # current pose-node

    def __init__(
            self,
            optimiser: tp.Optional[Optimiser] = None
    ):
        self._model = Model()

        if optimiser is None:
            optimiser = Optimiser()
        self._optimiser = optimiser
        super().__init__()

    def model(self) -> 'SubModel':
        return self._model

    def reset(self) -> None:
        super().reset()
        self._model.reset()

        # reset graph
        self._pose_ids = []
        self._current_node = self.add_pose_node(SE2.from_translation_angle_elements(0, 0, 0))
        self._current_node.fix()

    # sensors
    def add_sensor(
            self,
            sensor_name: str,
            sensor: 'SubSensor'
    ) -> None:
        self.model().add_sensor(sensor_name, sensor)

    # add elements
    def add_node_from_value(
            self,
            value: 'Quantity'
    ) -> 'SubNode':
        """ Creates and adds a new node from a given value. """
        return self.add_node(SpatialNodeFactory.from_value(None, value))

    def add_pose_node(
            self,
            pose: SE2
    ) -> 'NodeSE2':
        """ Creates and adds a new node from a given pose. """
        node: 'NodeSE2' = self.add_node_from_value(pose)
        self._pose_ids.append(node.get_id())
        self._current_node = node
        return node

    def add_edge_from_value(
            self,
            sensor_name: str,
            ids: tp.List[int],
            measurement: 'Quantity'
    ) -> 'SubEdge':
        """ Creates and adds a new edge between given nodes with a measurement from a sensor. """
        sensor: 'SubSensor' = self.model().get_sensor(sensor_name)
        graph: 'SubGraph' = self.graph()

        # create edge
        nodes: tp.List['SubNode'] = [graph.get_node(id_) for id_ in ids]
        edge: 'SubEdge' = EdgeFactory.from_measurement_nodes(
            sensor_name, measurement, nodes,
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
    ) -> tp.Tuple['NodeSE2', 'SubEdge']:
        """ Creates and adds a new node and edge with a measurement from a sensor. """
        sensor: 'SubSensor' = self.model().get_sensor(sensor_name)
        transformation: SE2 = sensor.compose(measurement)

        current: 'NodeSE2' = self._current_node
        pose: SE2 = current.get_value() + transformation
        new: 'NodeSE2' = self.add_pose_node(pose)
        edge: 'SubEdge' = self.add_edge_from_value(
            sensor_name,
            [current.get_id(), new.get_id()],
            measurement
        )
        return new, edge

    def add_odometry_to(
            self,
            sensor_name: str,
            pose: SE2
    ) -> tp.Tuple['SubNode', 'SubEdge']:
        """ Adds a new pose-node and edge at <pose>, as measured by <sensor_name>. """
        transformation: SE2 = pose - self._current_node.get_value()
        return self.add_odometry(sensor_name, transformation)

    # nodes
    def current(self) -> 'NodeSE2':
        """ Returns the current pose-node. """
        return self._current_node

    def pose_ids(self) -> tp.List[int]:
        """ Returns all previous pose-node ids. """
        return self._pose_ids

    # optimiser
    def has_optimiser(self) -> bool:
        """ Returns whether an optimiser has been set. """
        return self._optimiser is not None

    def set_optimiser(self, optimiser: Optimiser) -> None:
        """ Sets the optimiser. """
        self._optimiser = optimiser

    def get_optimiser(self) -> Optimiser:
        """ Returns the optimiser. """
        assert self.has_optimiser()
        return self._optimiser

    def set_previous(self, previous: 'SubGraph') -> None:
        """ Sets a previous graph. """
        self.graph().set_previous(previous)

    def add_static_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            index: int = 0
    ) -> 'SubParameterNode':
        parameter: 'SubParameter' = StaticParameter(
            self,
            value,
            specification,
            name=parameter_name,
            index=index,
            is_visible=True
        )
        return self._model.add_parameter(sensor_name, parameter_name, parameter)

    def update_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity'
    ) -> 'SubParameterNode':
        return self._model.update_parameter(sensor_name, parameter_name, value)

    @abstractmethod
    def step(self) -> 'SubGraph':
        """ Progresses (steps forward in time) the model. """
        pass

    @abstractmethod
    def report_closure(self) -> None:
        """ Registers the addition of a loop closure constraint. """
        pass


class PlainSimulation(Simulation):

    def __init__(self, optimiser: tp.Optional[Optimiser] = None):
        super().__init__(optimiser=optimiser)
        self.set_timestep(0)

    def step(self) -> 'SubGraph':
        snapshot: 'SubGraph' = self.graph().copy(is_shallow=True)
        self.set_previous(snapshot)

        self.increment_timestep()
        return snapshot

    def report_closure(self) -> None:
        pass


class OptimisingSimulation(Simulation, ABC):
    _has_closure: bool  # indicates whether a closure has occurred at this step
    _last_cost: tp.Optional[float]

    def __init__(self, optimiser: tp.Optional[Optimiser] = None):
        super().__init__(optimiser=optimiser)
        self._has_closure = False
        self._last_cost = None
        self.set_timestep(0)

    def reset(self) -> None:
        super().reset()
        self._has_closure = False
        self._last_cost = None

    def add_odometry(
            self,
            sensor_name: str,
            measurement: SE2
    ) -> tp.Tuple['SubNode', 'SubEdge']:
        self._has_closure = False
        return super().add_odometry(sensor_name, measurement)

    def report_closure(self) -> None:
        self._has_closure = True
        for sensor in self.model().get_sensors():
            for parameter in sensor.get_parameters():
                parameter.report_closure()

    def step(self) -> 'SubGraph':
        graph: 'SubGraph' = self.graph()
        solution: tp.Optional['SubGraph'] = None
        if self._has_closure:
            cost_threshold: tp.Optional[float] = 0.
            if self._last_cost is not None:
                cost_threshold = 2 * self._last_cost
            solution = graph.optimise(self.get_optimiser(), cost_threshold=cost_threshold)
            self._last_cost = solution.cost()
        if solution is None:
            solution = graph.copy()
        self.set_previous(solution)

        self.increment_timestep()
        return solution

    def add_timely_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            batch_size: int,
            index: int = 0
    ) -> 'SubParameterNode':
        parameter: 'SubParameter' = TimelyBatchParameter(
            self,
            value,
            specification,
            name=parameter_name,
            batch_size=batch_size,
            index=index
        )
        return self.model().add_parameter(sensor_name, parameter_name, parameter)

    def add_sliding_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            window: int,
            index: int = 0
    ) -> 'SubParameterNode':
        parameter: 'SubParameter' = SlidingParameter(
            self,
            value,
            specification,
            window,
            name=parameter_name,
            index=index
        )
        return self.model().add_parameter(sensor_name, parameter_name, parameter)

    def add_old_sliding_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            window_size: int,
            index: int = 0
    ) -> 'SubParameterNode':
        parameter: 'SubParameter' = OldSlidingParameter(
            self,
            value,
            specification,
            window_size,
            name=parameter_name,
            index=index
        )
        return self.model().add_parameter(sensor_name, parameter_name, parameter)


class PostSimulation(Simulation):
    _analyser: tp.Optional['SubPostAnalyser']
    _sensor_name: tp.Optional[str]

    def __init__(self, optimiser: tp.Optional[Optimiser] = None):
        super().__init__(optimiser=optimiser)
        self._analyser = None
        self._sensor_name = None

    def report_closure(self) -> None:
        pass

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

    def add_spatial_parameter(
            self,
            sensor_name: str,
            parameter_name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            num_batches: int,
            index: int = 0
    ):
        analyser: 'SubPostAnalyser' = SpatialBatchAnalyser(
            self,
            parameter_name,
            value,
            specification,
            num_batches,
            index=index
        )
        self.add_analyser(sensor_name, analyser)

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

    def step(self) -> 'SubGraph':
        self.increment_timestep()
        return self.graph()

    def post_process(
            self,
            steps: int = 1
    ) -> None:
        assert self.has_analyser()
        analyser: SubPostAnalyser = self.get_analyser()

        previous: 'SubGraph' = self.graph().optimise(self.get_optimiser(), cost_threshold=None)
        for _ in range(steps):
            self.set_previous(previous)
            analyser.post_process()
            previous = self.graph().optimise(self.get_optimiser(), cost_threshold=None)
