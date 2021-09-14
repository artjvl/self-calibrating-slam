import numpy as np
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3, Square2
from src.framework.math.matrix.vector import Vector1, Vector2, Vector3
from src.framework.simulation.Model2D import SubModel2D, PlainModel2D, IncrementalModel2D, SlidingModel2D
from framework.simulation.Simulation import ManhattanSimulation2D


def f_space(x, y):
    return -0.5 + 0.01 * (x + y)
    # return 0.1 * np.sin(0.1 * (x + y))


def f_time(x):
    return 0.1 * np.sin(0.02 * x)


class ManhattanSim(ManhattanSimulation2D):

    def configure(self) -> None:
        self.set_block_size(6)  # 6

        model: 'SubModel2D' = self.model()
        model.set_path_rng(33)  # 4, 33
        model.set_constraint_rng(0)
        model.set_sensor_seed(0)

        info_diagonal = Vector3([3600., 2500., 1600.])
        info_matrix3 = Square3.from_diagonal(info_diagonal.to_list())

        # wheel
        model.add_sensor('wheel', SE2, info_matrix3, info_matrix3)
        model.add_truth_parameter('wheel', 'bias', Vector1(0.2), ParameterSpecification.BIAS, index=0)
        model.add_truth_parameter('wheel', 'time', Vector1(0.01), ParameterSpecification.BIAS, index=2)

        # lidar
        model.add_sensor('lidar', SE2, info_matrix3, info_matrix3)

        # gps
        info_matrix2 = Square2.from_diagonal([800., 600.])
        model.add_sensor('gps', Vector2, info_matrix2, info_matrix2)

    def simulate(self) -> None:
        model: 'SubModel2D' = self.model()

        delta: float = 0.1
        for i in range(200):  # 400
            self.auto_odometry('wheel')
            # if i == 100:
                # self.update_truth_parameter('wheel', 'bias', Vector1(-0.2))
                # self.update_truth_parameter('wheel', 'bias', Vector1(0.1 * np.sin(0.01 * i)))
            model.roll_proximity('lidar', 3, threshold=0.8)
            model.roll_closure('lidar', 2., separation=10, threshold=0.2)

            model.update_truth_parameter('wheel', 'bias', Vector1(f_time(i)))
            # translation: Vector2 = self.get_current_pose().translation()
            # model.update_truth_parameter('wheel', 'bias', Vector1(f_space(translation[0], translation[1])))
            # model.update_constant_estimate_parameter('wheel', 'bias', Vector1(0.))

            model.step(delta)

    def finalise(self) -> None:
        pass


model: 'SubModel2D'

# plain
model = PlainModel2D()
manhattan_sim_plain = ManhattanSim('ManhattanSim: Plain', model)

# incremental
model = IncrementalModel2D()
manhattan_sim_inc = ManhattanSim('ManhattanSim: Incremental', model)
model.add_constant_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, index=0)

# sliding
model = SlidingModel2D()
manhattan_sim_sliding = ManhattanSim('ManhattanSim: Sliding', model)
model.add_sliding_estimate_parameter('wheel', 'bias', Vector2(0., 0.), ParameterSpecification.BIAS, 20, index=1)
