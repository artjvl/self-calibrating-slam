import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.parameter.ParameterNodeFactory import ParameterNodeFactory
from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification
from src.framework.math.matrix.vector.Vector import Vector

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubEdge, SubParameterNode
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.math.lie.transformation import SE2
    from src.framework.simulation.Simulation import SubSimulation

SubParameter = tp.TypeVar('SubParameter', bound='Parameter')


class Parameter(object):
    _sim: 'SubSimulation'
    _node: 'SubParameterNode'
    _is_visible: bool

    def __init__(
            self,
            simulation: 'SubSimulation',
            value: 'Quantity',
            specification: ParameterSpecification,
            name: tp.Optional[str] = None,
            index: int = 0,
            is_visible: bool = True
    ):
        self._sim = simulation
        self._is_visible = is_visible

        # create node
        if specification == ParameterSpecification.SCALE:
            assert isinstance(value, Vector)
            assert not any(np.isclose(element, 0.) for element in value.to_list())
        self._node = ParameterNodeFactory.from_value(
            name,
            value=value, specification=specification, index=index
        )
        self._sim.add_node(self._node)

    def simulation(self) -> 'SubSimulation':
        return self._sim

    @abstractmethod
    def add_edge(
            self,
            edge: 'SubEdge'
    ) -> None:
        pass

    def node(self) -> 'SubParameterNode':
        return self._node

    def set_name(self, name: str) -> None:
        self._node.set_name(name)

    def is_visible(self) -> bool:
        return self._is_visible

    @abstractmethod
    def report_closure(self) -> None:
        pass

    def compose(
            self,
            transformation: 'SE2',
            is_inverse: bool = False
    ) -> 'SE2':
        return self._node.compose_transformation(transformation, is_inverse)


class StaticParameter(Parameter):

    def update(
            self,
            value: 'Quantity'
    ) -> 'SubParameterNode':
        old: 'SubParameterNode' = self._node
        new: 'SubParameterNode' = old.__class__(
            value=value,
            name=old.get_name(),
            index=old.index(),
            specification=old.get_specification()
        )
        self.simulation().add_node(new)
        self._node = new
        return new

    def report_closure(self) -> None:
        pass

    def add_edge(
            self,
            edge: 'SubEdge'
    ) -> None:
        node: SubParameterNode = self.node()
        if self.is_visible():
            edge.add_node(node)
        else:
            edge.set_from_transformation(node.decompose(edge.to_transformation()))


class TimelyBatchParameter(StaticParameter):
    _batch_size: int
    _edge_count: int

    def __init__(
            self,
            simulation: 'SubSimulation',
            value: 'Quantity',
            specification: ParameterSpecification,
            batch_size: int,
            name: tp.Optional[str] = None,
            index: int = 0
    ):
        super().__init__(
            simulation,
            value,
            specification,
            name=name,
            index=index,
            is_visible=True
        )
        self._batch_size = batch_size

        self._edge_count = 0

    def renew(self) -> 'SubParameterNode':
        return self.update(self.node().get_value())

    def add_edge(
            self,
            edge: 'SubEdge'
    ) -> None:
        if self._edge_count == self._batch_size:
            self.renew()
            self._edge_count = 0
        edge.add_node(self.node())
        self._edge_count += 1


class SlidingParameter(Parameter):
    _window_size: int

    _in: tp.List['SubEdge']
    _is_closures: tp.List[bool]
    _between: tp.List['SubEdge']
    _out: tp.List['SubEdge']

    def __init__(
            self,
            simulation: 'SubSimulation',
            value: 'Quantity',
            specification: ParameterSpecification,
            window_size: int,
            name: tp.Optional[str] = None,
            index: int = 0
    ):
        super().__init__(
            simulation,
            value,
            specification,
            name=name,
            index=index,
            is_visible=True
        )
        self._window_size = window_size

        self._in = []
        self._is_closures = []
        self._between = []
        self._out = []

    def get_window(self) -> int:
        return self._window_size

    def report_closure(self) -> None:
        self._is_closures[-1] = True

    def add_edge(
            self,
            edge: 'SubEdge'
    ) -> None:
        node: 'SubParameterNode' = self.node()
        edge.add_node(node)

        if len(self._in) < self._window_size:
            self._in.append(edge)  # append <node>
            self._is_closures.append(False)  # append <is_closure>
        else:
            self._between = self._between + self._in[:1]  # push in first element of <_in>
            self._in = self._in[1:] + [edge]  # push in <node> and push out first element
            self._is_closures = self._is_closures[1:] + [False]  # push in <is_closure> and push out first element

        # if any closures are present in the previously connected edges, the window size is reduced to its default value
        if len(self._is_closures) > 1 and self._is_closures[-2]:
            for edge_ in self._between:
                edge_.remove_node_id(node.get_id())
                edge_.set_from_transformation(node.compose_transformation(edge_.to_transformation(), is_inverse=False))
                self._out.append(edge_)
            self._between = []


class OldSlidingParameter(Parameter):
    _window_size: int

    _in: tp.List['SubEdge']
    _out: tp.List['SubEdge']

    def __init__(
            self,
            simulation: 'SubSimulation',
            value: 'Quantity',
            specification: ParameterSpecification,
            window_size: int,
            name: tp.Optional[str] = None,
            index: int = 0
    ):
        super().__init__(
            simulation,
            value,
            specification,
            name=name,
            index=index,
            is_visible=True
        )
        self._window_size = window_size

        self._in = []
        self._out = []

    def get_window(self) -> int:
        return self._window_size

    def report_closure(self) -> None:
        pass

    def add_edge(
            self,
            edge: 'SubEdge'
    ) -> None:
        node: 'SubParameterNode' = self.node()
        edge.add_node(node)

        self._in.append(edge)
        if len(self._in) > self._window_size:
            first: 'SubEdge' = self._in[0]
            first.remove_node_id(node.get_id())
            first.set_from_transformation(node.compose_transformation(first.to_transformation(), is_inverse=False))
            self._in = self._in[1:]
