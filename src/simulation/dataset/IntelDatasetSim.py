import pathlib

import numpy as np
from src.definitions import get_project_root
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector1
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3
from src.framework.simulation.Model2D import SubModel2D, PlainModel2D, IncrementalModel2D, SlidingModel2D
from src.framework.simulation.Simulation import InputSimulation2D


def f_time(x):
    return 0.1 * np.sin(0.02 * x)


class IntelDatasetSim(InputSimulation2D):

    def configure(self) -> None:
        root: pathlib.Path = get_project_root()
        path: pathlib.Path = (root / 'graphs/solution_INTEL_g2o.g2o').resolve()
        self.set_path(path)

        model: 'SubModel2D' = self.model()
        model.set_constraint_rng(5)
        model.set_sensor_seed(1)

        info_diagonal = Vector3([900., 625., 400.])
        info_matrix3 = Square3.from_diagonal(info_diagonal.to_list())

        # wheel
        model.add_sensor('wheel', SE2, info_matrix3, info_matrix3)
        model.add_truth_parameter('wheel', 'bias', Vector1(0.2), ParameterSpecification.BIAS, index=0)
        model.add_truth_parameter('wheel', 'time', Vector1(0.1), ParameterSpecification.BIAS, index=2)

        # model.add_truth_parameter('wheel', 'bias', Vector1(-0.1), ParameterSpecification.BIAS, index=1)
        # model.add_truth_parameter('wheel', 'bias', Vector2(0.1, -0.2), ParameterSpecification.BIAS, index=2)

        # lidar
        model.add_sensor('lidar', SE2, info_matrix3, info_matrix3)

    def simulate(self) -> None:
        model: 'SubModel2D' = self.model()

        delta: float = 0.1
        for i in range(300):
        # while self.has_next():
            self.auto_odometry('wheel')
            model.update_truth_parameter('wheel', 'bias', Vector1(f_time(i)))
            model.roll_proximity('lidar', 3, threshold=0.6)
            model.roll_closure('lidar', 2., separation=10, threshold=0.2)
            model.step(delta)

    def finalise(self) -> None:
        pass


model: 'SubModel2D'

# plain
model = PlainModel2D()
intel_sim_plain = IntelDatasetSim('IntelSim: Plain', model)

# incremental
model = IncrementalModel2D()
intel_sim_inc = IntelDatasetSim('IntelSim: Incremental', model)
# model.add_constant_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, index=0)
model.add_constant_estimate_parameter('wheel', 'bias', Vector2(0., 0.), ParameterSpecification.BIAS, index=1)
# model.add_sliding_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, 40, index=1)

# sliding
model = SlidingModel2D()
intel_sim_sliding = IntelDatasetSim('IntelSim: Sliding', model)
# model.add_constant_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, index=1)
# model.add_sliding_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, 20, index=1)
model.add_sliding_estimate_parameter('wheel', 'bias', Vector2(0., 0.), ParameterSpecification.BIAS, 40, index=1)

# old sliding
model = SlidingModel2D()
intel_sim_old_sliding = IntelDatasetSim('IntelSim: Sliding (old)', model)
# model.add_constant_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, index=1)
model.add_old_sliding_estimate_parameter('wheel', 'bias', Vector1(0.), ParameterSpecification.BIAS, 40, index=1)
