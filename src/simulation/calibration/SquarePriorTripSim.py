import numpy as np
from src.framework.graph.types.scslam2d.nodes.parameter import ParameterNodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square2
from src.framework.math.matrix.square import Square3
from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.framework.simulation.sensors import SensorV2
from src.framework.simulation.sensors.SensorSE2 import SensorSE2


class SquarePriorTripSim(BiSimulation2D):

    # constructor
    def __init__(self):
        super().__init__()

    # public methods
    def _simulate(self):

        info_matrix3 = Square3([[800., 0., 0.], [0., 600., 0.], [0., 0., 400.]])
        true_odo_par = ParameterNodeSE2()
        true_odo_par.set_value(SE2.from_translation_angle_elements(0.0, 0.2, 0.))
        true_odo_par.set_as_bias()
        true_odo = SensorSE2()
        true_odo.add_parameter(true_odo_par)
        true_odo.set_info_matrix(info_matrix3)
        perturbed_odo_par = ParameterNodeSE2()
        # perturbed_odo_par.fix()
        perturbed_odo_par.set_value(SE2.from_translation_angle_elements(0., 0., 0.))
        perturbed_odo_par.set_as_bias()
        perturbed_odo = SensorSE2()
        perturbed_odo.add_parameter(perturbed_odo_par)
        perturbed_odo.set_info_matrix(info_matrix3)
        self.add_sensor('lidar', true_odo, perturbed_odo)

        info_matrix2 = Square2([[800., 0.], [0., 600.]])
        true_gps = SensorV2()
        true_gps.set_info_matrix(info_matrix2)
        perturbed_gps = SensorV2()
        perturbed_gps.set_info_matrix(info_matrix2)
        self.add_sensor('gps', true_gps, perturbed_gps)

        angle: float
        num = 5
        for _ in range(4):
            for __ in range(num):
                angle = np.deg2rad(90) if __ == num - 1 else 0.
                motion = SE2.from_translation_angle_elements(1.0, 0, angle)
                self.add_odometry('lidar', motion)
            if _ % 2 == 0:
                self.add_gps('gps')
