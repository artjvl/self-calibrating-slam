from src.framework.math.matrix.square import Square2
from src.framework.simulation.sensors import SensorV2
from src.framework.graph.types.scslam2d.nodes.parameter import ParameterNodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.framework.simulation.sensors.SensorSE2 import SensorSE2


class SingleTripSim(BiSimulation2D):

    def _simulate(self) -> None:

        info_matrix3 = Square3([[8000., 0., 0.], [0., 6000., 0.], [0., 0., 4000.]])
        true_wheel_par = ParameterNodeSE2()
        true_wheel_par.set_value(SE2.from_translation_angle_elements(0.0, 0.0, 0.))
        true_wheel_par.set_as_bias()
        true_wheel = SensorSE2()
        true_wheel.add_parameter(true_wheel_par)
        true_wheel.set_info_matrix(info_matrix3)
        perturbed_wheel_par = ParameterNodeSE2()
        perturbed_wheel_par.set_value(SE2.from_translation_angle_elements(0., 0.2, 0.))
        perturbed_wheel_par.set_as_bias()
        perturbed_wheel = SensorSE2()
        perturbed_wheel.add_parameter(perturbed_wheel_par)
        perturbed_wheel.set_info_matrix(info_matrix3)
        self.add_sensor('wheel', true_wheel, perturbed_wheel)

        info_matrix2 = Square2([[8000., 0.], [0., 6000.]])
        true_gps = SensorV2()
        true_gps.set_info_matrix(info_matrix2)
        perturbed_gps = SensorV2()
        perturbed_gps.set_info_matrix(info_matrix2)
        self.add_sensor('gps', true_gps, perturbed_gps)

        num = 10
        for _ in range(num):
            motion = SE2.from_translation_angle_elements(1.0, 0, 0.)
            self.add_odometry('wheel', motion)
        self.add_gps('gps')
