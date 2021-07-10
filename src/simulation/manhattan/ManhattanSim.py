import numpy as np
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3, Square2
from src.framework.math.matrix.vector import Vector3
from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.framework.simulation.sensors import SensorSE2
from src.framework.simulation.sensors import SensorV2


class ManhattanSim(BiSimulation2D):

    def _simulate(self) -> None:
        self.set_seed(3)

        info_diagonal = Vector3([900., 625., 400.])
        info_matrix3 = Square3.from_diagonal(info_diagonal.to_list())

        # true
        true_odo = SensorSE2()
        true_odo.set_info_matrix(info_matrix3)
        true_odo.add_offset('offset', SE2.from_translation_angle_elements(-0.1, 0.2, 0.))
        # true_odo.add_scale('scale', Vector3(1.1, 1.2, 1.))

        # perturbed
        perturbed_odo = SensorSE2()
        perturbed_odo.set_info_matrix(info_matrix3)
        perturbed_odo.add_offset('offset', SE2.from_translation_angle_elements(0., 0., 0.))
        # perturbed_odo.add_scale('scale', Vector3(1., 1., 1.))

        self.add_sensor('wheel', true_odo, perturbed_odo)

        true_scan = SensorSE2()
        true_scan.set_info_matrix(info_matrix3)
        perturbed_scan = SensorSE2()
        perturbed_scan.set_info_matrix(info_matrix3)
        self.add_sensor('lidar', true_scan, perturbed_scan)

        info_matrix2 = Square2.from_diagonal([800., 600.])
        true_gps = SensorV2()
        true_gps.set_info_matrix(info_matrix2)
        perturbed_gps = SensorV2()
        perturbed_gps.set_info_matrix(info_matrix2)
        self.add_sensor('gps', true_gps, perturbed_gps)

        num: int = 5
        angle: float
        for _ in range(50):
            for __ in range(num):
                angle = np.deg2rad(self.get_rng().choice([90, -90])) if __ == num - 1 else 0.
                motion = SE2.from_translation_angle_elements(1.0, 0.1, angle)
                if _ == 5 and __ == 0:
                    i = 0
                self.add_odometry('wheel', motion)
                self.roll_proximity('lidar', 5, threshold=0.4)
                self.roll_closure('lidar', 3., threshold=0.4)
