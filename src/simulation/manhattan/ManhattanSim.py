import numpy as np
from src.framework.graph.types.scslam2d.nodes.parameter import ParameterNodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3, Square2
from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.framework.simulation.sensors import SensorSE2
from src.framework.simulation.sensors import SensorV2


class ManhattanSim(BiSimulation2D):

    def _simulate(self) -> None:

        info_matrix3 = Square3.from_diagonal([200., 160., 120.])
        true_odo_par = ParameterNodeSE2()
        true_odo_par.set_value(SE2.from_translation_angle_elements(-0.1, 0.2, 0.))
        true_odo_par.set_as_bias()
        true_odo = SensorSE2()
        true_odo.add_parameter(true_odo_par)
        true_odo.set_info_matrix(info_matrix3)
        perturbed_odo_par = ParameterNodeSE2()
        perturbed_odo_par.set_value(SE2.from_translation_angle_elements(0., 0., 0.))
        perturbed_odo_par.set_as_bias()
        perturbed_odo = SensorSE2()
        perturbed_odo.add_parameter(perturbed_odo_par)
        perturbed_odo.set_info_matrix(info_matrix3)
        self.add_sensor('wheel', true_odo, perturbed_odo)

        info_matrix3 = Square3.from_diagonal([800., 600., 400.])
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
        for _ in range(60):
            for __ in range(num):
                angle = np.deg2rad(np.random.choice([90, -90])) if __ == num - 1 else 0.
                motion = SE2.from_translation_angle_elements(1.0, 0, angle)
                self.add_odometry('wheel', motion)
                self.roll_proximity('lidar', 5, threshold=0.4)
                self.roll_closure('lidar', 3., threshold=0.4)
