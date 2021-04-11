import typing as tp
from abc import abstractmethod

import numpy as np
from numpy.random.mtrand import RandomState

from src.framework.graph.data import SubData
from src.framework.graph.data.DataFactory import DataFactory
from src.framework.graph.types.scslam2d.edges.CalibratingEdge import SubCalibratingEdge
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import SubInformationNode
from src.framework.graph.types.scslam2d.nodes.parameter.ParameterNode import SubParameterNode
from src.framework.math.matrix.square import SubSquare, SquareFactory
from src.framework.math.matrix.vector import SubVector, VectorFactory

T = tp.TypeVar('T')
SubSensor = tp.TypeVar('SubSensor', bound='Sensor')


class Sensor(tp.Generic[T]):

    _type: tp.Type[T]

    def __init__(
            self,
            seed: int = 0,
            matrix: tp.Optional[SubSquare] = None
    ):
        self._rng = np.random.RandomState(seed)

        # information
        if matrix is None:
            matrix = SquareFactory.from_dim(self.get_dimension()).identity()
        self._matrix: SubSquare = matrix

        # parameter
        self._parameters: tp.List[SubParameterNode] = []
        self._information: tp.Optional[SubInformationNode] = None

    # measurement-type
    @classmethod
    def get_dimension(cls):
        return DataFactory.from_type(cls.get_type()).get_length()

    @classmethod
    def get_type(cls) -> tp.Type[SubData]:
        return cls._type

    # parameter
    def add_parameter(
            self,
            parameter: SubParameterNode
    ) -> None:
        self._parameters.append(parameter)

    def get_parameters(self) -> tp.List[SubParameterNode]:
        return self._parameters

    # information
    def add_information(
            self,
            node: SubInformationNode
    ) -> None:
        assert self.get_dimension() == node.get_dimension()
        self._information = node
        # self._matrix = SquareFactory.from_dim(self.get_dimension()).identity()

    def get_information(self) -> SubInformationNode:
        assert self.has_information()
        return self._information

    def has_information(self) -> bool:
        return self._information is not None

    def get_matrix(self) -> SubSquare:
        if self.has_information():
            return self._information.get_matrix()
        return self._matrix

    # noise
    def generate_noise(self) -> SubVector:
        dim: int = self.get_dimension()
        vector_type: tp.Type[SubVector] = VectorFactory.from_dim(dim)
        return vector_type(
            self._rng.multivariate_normal(
                mean=[0] * dim,
                cov=self.get_matrix().inverse().array()
            )
        )

    @abstractmethod
    def measure(self, value: T) -> T:
        pass

    @abstractmethod
    def compose(self, value: T) -> T:
        pass

    def compose_edge(
            self,
            edge: SubCalibratingEdge,
            value: T
    ) -> SubCalibratingEdge:
        assert edge.get_type() == self.get_type()

        # set measurement
        measurement: T = self.compose(value)
        edge.set_measurement(measurement)

        # add parameters
        for parameter in self._parameters:
            edge.add_parameter(parameter)

        # add information
        edge.set_information(self._matrix)
        if self.has_information():
            edge.add_info_node(self._information)

        return edge
