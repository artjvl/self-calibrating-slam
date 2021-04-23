from typing import *

import numpy as np
from src.framework.graph.Graph import Graph
from src.framework.graph.types.scslam2d.nodes.parameter import ParameterNodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.framework.simulation.sensors.SensorSE2 import SensorSE2


class CalibrationSimulation(BiSimulation2D):

    # constructor
    def __init__(self):
        super().__init__()

    # public methods
    def _simulate(self) -> Tuple[Graph, Graph]:

        # info = InformationNodeFull3()
        # info.set_value(Vector6([800, 0, 0, 600, 0, 400]))
        info_matrix = Square3([[800, 0, 0], [0, 600, 0], [0, 0, 400]])

        true_par = ParameterNodeSE2()
        true_par.set_value(SE2.from_translation_angle_elements(0.0, 0.4, 0.00))
        true_par.set_as_bias()
        true = SensorSE2()
        true.add_parameter(true_par)
        true.set_information(info_matrix)

        perturbed_par = ParameterNodeSE2()
        perturbed_par.set_value(SE2.from_translation_angle_elements(0.0, 0.0, 0.00))
        perturbed_par.set_as_bias()
        perturbed = SensorSE2()
        # perturbed.add_parameter(perturbed_par)
        perturbed.set_information(info_matrix)

        self.add_sensor('lidar', true, perturbed)

        angle: float = 0
        num = 10
        for _ in range(2):
            for __ in range(num):
                angle: float = np.deg2rad(180.) if __ == num - 1 else 0.
                motion = SE2.from_translation_angle_elements(1.0, 0, angle)
                self.add_odometry(motion, 'lidar')
            self.add_closure(1, 'lidar')


        # motion = SE2.from_translation_angle_elements(1.0, 0, angle)
        # self.add_odometry(motion, 'lidar')
        # self.fix()

        # self.add_poses_edge(1, 4, 'lidar')

        return self.get_graphs()
