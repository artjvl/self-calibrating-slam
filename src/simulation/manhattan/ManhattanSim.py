import typing as tp

import numpy as np
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3, Square2
from src.framework.math.matrix.vector import Vector1
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3
from src.framework.simulation.simulations.ManhattanSimulation2D import ManhattanSimulation2D


def f_space(x, y):
    return -0.5 + 0.01 * (x + y)
    # return 0.1 * np.sin(0.1 * (x + y))


def f_time(x):
    return 0.1 * np.sin(0.1 * x)


class ManhattanSim(ManhattanSimulation2D):

    def init(self) -> None:
        self.set_path_rng(4)
        self.set_sensor_seed(1)

        info_diagonal = Vector3([900., 625., 400.])
        info_matrix3 = Square3.from_diagonal(info_diagonal.to_list())

        # wheel
        self.add_sensor('wheel', SE2, info_matrix3, info_matrix3)
        self.add_truth_parameter('wheel', 'bias', Vector1(-0.2), ParameterSpecification.BIAS, index=1)
        # self.add_truth_parameter('wheel', 'bias', Vector2(0.1, -0.2), ParameterSpecification.BIAS, index=2)

        # lidar
        self.add_sensor('lidar', SE2, info_matrix3, info_matrix3)

        # gps
        info_matrix2 = Square2.from_diagonal([800., 600.])
        self.add_sensor('gps', Vector2, info_matrix2, info_matrix2)

    def loop(self) -> None:

        delta: float = 0.1
        for i in range(100):
            self.auto_odometry('wheel')
            # self.update_truth_parameter('wheel', 'bias', Vector1(0.1 * np.sin(0.01 * i)))
            self.roll_proximity('lidar', 3, threshold=0.8)
            self.roll_closure('lidar', 1., threshold=0.2)

            # translation: Vector2 = self.get_current_pose().translation()
            # self.update_truth_parameter('wheel', 'bias', Vector1(f_time(i * delta)))
            # self.update_truth_parameter('wheel', 'bias', Vector1(f_space(translation[0], translation[1])))
            # self.update_constant_estimate_parameter('wheel', 'bias', Vector1(0.))

            self.step(delta)

        # import matplotlib.pyplot as plt
        # grid_x, grid_y = np.mgrid[-15:50:131j, 0:65:131j]
        # plt.imshow(f_space(grid_x, grid_y).T, extent=(-15, 50, 0, 65), origin='lower')
        # plt.show()
