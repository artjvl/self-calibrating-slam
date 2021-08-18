import numpy as np
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square2
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector2
from src.framework.simulation.BiSimulation2D import BiSimulation2D


class SquarePriorTripSim(BiSimulation2D):

    def init(self) -> None:
        info_matrix3 = Square3([[8000., 0., 0.], [0., 6000., 0.], [0., 0., 4000.]])
        self.add_sensor('lidar', SE2, info_matrix3, info_matrix3)
        self.add_truth_parameter(
            'lidar', 'bias',
            SE2.from_translation_angle_elements(0., 0., 0.), ParameterSpecification.BIAS
        )
        self.add_constant_estimate_parameter(
            'lidar', 'bias',
            SE2.from_translation_angle_elements(0., 0.2, 0.), ParameterSpecification.BIAS
        )
        info_matrix2 = Square2([[800., 0.], [0., 600.]])
        self.add_sensor('gps', Vector2, info_matrix2, info_matrix2)

    def loop(self):
        angle: float
        num = 5
        for _ in range(4):
            for __ in range(num):
                angle = np.deg2rad(90) if __ == num - 1 else 0.
                motion = SE2.from_translation_angle_elements(1.0, 0, angle)
                self.add_odometry('lidar', motion)
            if _ % 2 == 0:
                self.add_gps('gps')
