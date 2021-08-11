import numpy as np
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.simulation.BiSimulation2D import BiSimulation2D


class ReturnTripSim(BiSimulation2D):

    def _simulate(self) -> None:

        info_matrix3 = Square3([[8000., 0., 0.], [0., 6000., 0.], [0., 0., 4000.]])
        true_lidar = SensorSE2()
        true_lidar.add_bias('bias', SE2.from_translation_angle_elements(0.0, 0.0, 0.))
        true_lidar.set_info_matrix(info_matrix3)
        perturbed_lidar = SensorSE2()
        perturbed_lidar.add_bias('bias', SE2.from_translation_angle_elements(0., 0.2, 0.))
        perturbed_lidar.set_info_matrix(info_matrix3)
        self.add_sensor('lidar', true_lidar, perturbed_lidar)

        num = 10
        for _ in range(2):
            for __ in range(num):
                angle: float = np.deg2rad(180.) if __ == num - 1 else 0.
                motion = SE2.from_translation_angle_elements(1.0, 0, angle)
                self.add_odometry('lidar', motion)
            self.try_closure('lidar', 1.)
