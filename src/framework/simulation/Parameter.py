import typing as tp
from abc import abstractmethod

from src.framework.graph.types.nodes.ParameterNode import ParameterNodeFactory, ParameterNodeV1, \
    ParameterNodeV2

if tp.TYPE_CHECKING:
    from src.framework.graph.CalibratingGraph import SubCalibratingEdge
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.protocols.Measurement2D import SubMeasurement2D
    from src.framework.graph.types.nodes.ParameterNode import SubParameterNode, ParameterSpecification

SubParameterModel = tp.TypeVar('SubParameterModel', bound='ParameterModel')


class Parameter(object):
    _node: 'SubParameterNode'
    _is_visible: bool

    def __init__(
            self,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            index: int = 0,
            is_visible: bool = True
    ):
        # create node
        node: SubParameterNode = ParameterNodeFactory.from_value(
            value=value,
            specification=specification
        )
        if isinstance(node, (ParameterNodeV1, ParameterNodeV2)):
            node.set_index(index)
        self._node = node

        # metadata
        self._is_visible = is_visible

    @abstractmethod
    def add_edge(self, edge: 'SubCalibratingEdge') -> None:
        pass

    def get_node(self) -> 'SubParameterNode':
        return self._node

    def set_name(self, name: str) -> None:
        self._node.set_name(name)

    def is_visible(self) -> bool:
        return self._is_visible

    def compose(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        return self._node.compose(measurement, is_inverse)


class StaticParameter(Parameter):

    def update(
            self,
            value: 'Quantity'
    ) -> 'SubParameterNode':
        old: 'SubParameterNode' = self._node
        new: 'SubParameterNode' = old.__class__(
            value=value,
            specification=old.get_specification(),
            name=old.get_name()
        )
        self._node = new
        return new

    def add_edge(self, edge: 'SubCalibratingEdge') -> None:
        node: SubParameterNode = self.get_node()
        if self.is_visible():
            edge.add_parameter(node)
        else:
            edge.set_measurement(node.decompose(edge.get_measurement()))


class SlidingParameter(Parameter):
    _window: int
    _in: tp.List['SubCalibratingEdge']
    _out: tp.List['SubCalibratingEdge']

    def __init__(
            self,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            window: int,
            index: int = 0
    ):
        super().__init__(
            value=value,
            specification=specification,
            index=index,
            is_visible=True
        )
        self._window = window

    def get_window(self) -> int:
        return self._window

    def add_edge(self, edge: 'SubCalibratingEdge') -> None:
        node: SubParameterNode = self.get_node()
        edge.add_parameter(node)
        self._in.append(edge)

        if len(self._in) > self._window:
            first: 'SubCalibratingEdge' = self._in[0]
            first.remove_parameter_id(node.get_id())
            first.set_measurement(node.decompose(first.get_measurement()))
            self._out.append(first)
            self._in = self._in[1:]
