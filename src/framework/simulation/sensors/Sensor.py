import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.CalibratingGraph import SubCalibratingEdge
from src.framework.graph.Graph import SubGraph
from src.framework.graph.GraphManager import SubGraphManager
from src.framework.graph.data import SubData
from src.framework.graph.data.DataFactory import DataFactory
from src.framework.graph.types.ParameterComposer import ParameterType
from src.framework.graph.types.nodes.ParameterNode import SubParameterNode, ParameterData, ParameterNodeFactory, \
    ParameterV1
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import SubSquare, SquareFactory
from src.framework.math.matrix.vector import SubVector, VectorFactory
from src.framework.math.matrix.vector import Vector3

if tp.TYPE_CHECKING:
    pass

T = tp.TypeVar('T')
SubSensor = tp.TypeVar('SubSensor', bound='Sensor')


class Sensor(tp.Generic[T]):

    _type: tp.Type[T]
    _rng: np.random.RandomState

    _info_matrix: SubSquare
    _parameters: tp.Dict[str, SubParameterNode]

    _manager: tp.Optional[SubGraphManager]

    def __init__(
            self,
            seed: tp.Optional[int] = None,
            info_matrix: tp.Optional[SubSquare] = None
    ):
        self.set_seed(seed)

        # information
        if info_matrix is None:
            info_matrix = SquareFactory.from_dim(self.get_dim()).identity()
        self._info_matrix = info_matrix

        # parameter
        self._parameters = {}
        self._info_node = None
        self._info_edge = None

        # simulation
        self._manager = None

    # measurement-type
    @classmethod
    def get_dim(cls):
        return DataFactory.from_type(cls.get_type()).get_dim()

    @classmethod
    def get_type(cls) -> tp.Type[SubData]:
        return cls._type

    # simulation
    def has_graph(self) -> bool:
        return self._manager is not None

    def set_graph(self, manager: SubGraphManager) -> None:
        self._manager = manager

    # parameter
    def add_bias(
            self,
            name: str,
            value: ParameterData,
            index: int = 0
    ) -> SubParameterNode:
        assert name not in self._parameters
        parameter: SubParameterNode = ParameterNodeFactory.from_value(
            value,
            interpretation=ParameterType.BIAS,
            name=name
        )
        if isinstance(parameter, ParameterV1):
            parameter.set_index(index)
        self._parameters[name] = parameter
        return parameter

    def add_offset(
            self,
            name: str,
            value: ParameterData,
            index: int = 0
    ) -> SubParameterNode:
        assert name not in self._parameters
        parameter: SubParameterNode = ParameterNodeFactory.from_value(
            value,
            interpretation=ParameterType.OFFSET,
            name=name
        )
        if isinstance(parameter, ParameterV1):
            parameter.set_index(index)
        self._parameters[name] = parameter
        return parameter

    def add_scale(
            self,
            name: str,
            value: ParameterData,
            index: int = 0
    ) -> SubParameterNode:
        assert name not in self._parameters
        parameter: SubParameterNode = ParameterNodeFactory.from_value(
            value,
            interpretation=ParameterType.SCALE,
            name=name
        )
        if isinstance(parameter, ParameterV1):
            parameter.set_index(index)
        self._parameters[name] = parameter
        return parameter

    def get_parameter(self, name: str) -> SubParameterNode:
        assert name in self._parameters
        return self._parameters[name]

    def get_parameters(self) -> tp.List[SubParameterNode]:
        return list(self._parameters.values())

    def update_parameter(
            self,
            name: str,
            value: ParameterData,
            index: int = 0
    ) -> None:
        parameter: SubParameterNode = self.get_parameter(name)
        new: SubParameterNode = type(parameter)(
            value=value,
            interpretation=parameter.get_interpretation(),
            name=parameter.get_name()
        )
        if isinstance(new, ParameterV1):
            new.set_index(index)
        self._parameters[name] = new
        return new

    # info
    def set_info_matrix(self, info_matrix: SubSquare) -> None:
        self._info_matrix = info_matrix

    def get_info_matrix(self) -> SubSquare:
        return self._info_matrix

    # noise
    def set_seed(self, seed: tp.Optional[int] = None):
        self._rng = np.random.RandomState(seed)

    def generate_noise(self) -> SubVector:
        dim: int = self.get_dim()
        vector_type: tp.Type[SubVector] = VectorFactory.from_dim(dim)
        return vector_type(
            self._rng.multivariate_normal(
                mean=[0] * dim,
                cov=self.get_info_matrix().inverse().array()
            )
        )

    @abstractmethod
    def measure(self, value: T) -> T:
        """ Adds noise to the value. """
        pass

    @abstractmethod
    def compose(self, value: T) -> T:
        """ Composes the value by sequentially adding all stored parameters. """
        pass

    @abstractmethod
    def decompose(self, value: T) -> T:
        """ Decomposes the value by, in reverse order, subtracting all stored parameters. """
        pass

    def extend_edge(
            self,
            edge: SubCalibratingEdge
    ) -> SubCalibratingEdge:
        assert edge.get_type() == self.get_type()
        assert self.has_graph()

        # add parameters
        for parameter in self.get_parameters():
            graph: SubGraph = self._manager.get_graph()
            if not graph.contains_node(parameter):
                self._manager.add_node(parameter)
            if not edge.contains_node(parameter):
                edge.add_parameter(parameter)

        # add information
        edge.set_info_matrix(self._info_matrix)
        return edge
