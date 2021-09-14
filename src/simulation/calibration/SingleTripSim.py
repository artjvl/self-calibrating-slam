from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square2
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector2
from src.framework.simulation.Model2D import Model2D


class SingleTripSim(Model2D):

    def pre(self) -> None:
        info_matrix3 = Square3.from_diagonal([800., 600., 400.])
        self.add_sensor('wheel', SE2, info_matrix3, info_matrix3)
        self.add_truth_parameter(
            'wheel', 'bias',
            SE2.from_translation_angle_elements(0., 0., 0.), ParameterSpecification.BIAS
        )
        self.add_constant_estimate_parameter(
            'wheel', 'bias',
            SE2.from_translation_angle_elements(0., 0.2, 0.), ParameterSpecification.BIAS
        )

        info_matrix2 = Square2([[8000., 0.], [0., 6000.]])
        self.add_sensor('gps', Vector2, info_matrix2, info_matrix2)

    def loop(self) -> None:
        num = 10
        for _ in range(num):
            motion = SE2.from_translation_angle_elements(1.0, 0, 0.)
            self.add_odometry('wheel', motion)
        self.add_gps('gps')
