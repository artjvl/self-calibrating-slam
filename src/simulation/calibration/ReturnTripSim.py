import numpy as np
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.simulation.Model2D import Model2D


class ReturnTripSim(Model2D):

    def pre(self) -> None:
        self.add_sensor(
            'lidar', SE2,
            Square3.from_diagonal([800., 600., 400.]),
            Square3.from_diagonal([800., 600., 400.])
        )
        self.add_truth_parameter(
            'lidar', 'bias',
            SE2.from_translation_angle_elements(0., 0., 0.), ParameterSpecification.BIAS
        )
        self.add_constant_estimate_parameter(
            'lidar', 'bias',
            SE2.from_translation_angle_elements(0., 0.2, 0.), ParameterSpecification.BIAS
        )

    def loop(self) -> None:
        num: int = 10
        angle: float = 0.
        for _ in range(2):
            for __ in range(num):
                motion = SE2.from_translation_angle_elements(1.0, 0, angle)
                self.add_odometry('lidar', motion)
            angle += np.deg2rad(180)
