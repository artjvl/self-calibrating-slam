import pathlib

from src.framework.math.lie.transformation import SE2
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.matrix.vector import Vector1
from src.definitions import get_project_root
from src.framework.graph.GraphParser import GraphParser
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector3
from src.framework.simulation.simulations.InputSimulation2D import InputSimulation2D


class IntelDatasetSimulation(InputSimulation2D):

    def __init__(self):
        super().__init__()
        root: pathlib.Path = get_project_root()
        path: pathlib.Path = (root / 'graphs/solution_INTEL_g2o.g2o').resolve()
        self.set_input_graph(GraphParser.load(path))

    def _simulate(self) -> None:
        info_diagonal = Vector3([900., 625., 400.])
        info_matrix3 = Square3.from_diagonal(info_diagonal.to_list())

        # wheel
        self.add_sensor('wheel', SE2, info_matrix3, info_matrix3)
        # self.add_truth_parameter('wheel', 'bias', Vector1(-0.2), ParameterSpecification.BIAS, index=1)
        # self.add_truth_parameter('wheel', 'bias', Vector2(0.1, -0.2), ParameterSpecification.BIAS, index=2)
        # self.add_constant_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, index=1)
        # self.add_sliding_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, 40, index=1)

        # lidar
        self.add_sensor('lidar', SE2, info_matrix3, info_matrix3)

        delta: float = 0.1
        while self.has_next():
            self.auto_odometry('wheel')
            # self.roll_proximity('lidar', 3, threshold=0.8)
            self.roll_closure('lidar', 2., threshold=0.8)
            self.step(delta)
