import pathlib

import numpy as np
from src.definitions import get_project_root
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square2, Square3
from src.framework.math.matrix.vector import Vector1, Vector2
from src.framework.simulation.BiSimulation import BiSimulation
from src.framework.simulation.Path import InputPath


def f_step(x):
    if x > 100:
        return 0.1
    return -0.2


def f_sin(x):
    return 0.1 * np.sin(0.02 * x)


class IntelSim(BiSimulation):

    def configure(self) -> None:
        path: InputPath = InputPath()
        root: pathlib.Path = get_project_root()
        path.set_input_file((root / 'graphs/solution_INTEL_g2o.g2o').resolve())
        self.set_path(path)

        # seed
        self.set_sensor_seed(0)
        self.set_constraint_rng(0)

    def initialise(self) -> None:
        # sensors: wheel
        info_wheel_truth = Square3.from_diagonal([2000., 2000., 2000.])
        info_wheel_estimate = info_wheel_truth
        self.add_sensor('wheel', SE2, info_wheel_truth, info_wheel_estimate)
        # sensors: lidar
        info_lidar_truth = Square3.from_diagonal([8000., 8000., 12000.])
        info_lidar_estimate = info_lidar_truth
        self.add_sensor('lidar', SE2, info_lidar_truth, info_lidar_estimate)
        # sensors: gps
        info_gps_truth = Square2.from_diagonal([1., 1.])
        info_gps_estimate = info_gps_truth
        self.add_sensor('gps', Vector2, info_gps_truth, info_gps_estimate)

        # parameters:
        self.truth_simulation().add_static_parameter(
            'wheel', 'bias',
            Vector1(0.1), ParameterSpecification.BIAS, index=0
        )

    def simulate(self) -> None:
        delta: float = 0.1
        num: int = 100  # 400

        is_gps: bool = True
        is_dyn: bool = True

        gps_num: int = 10
        gps_ids: set = set(self.get_constraint_rng().randint(1, num, size=(gps_num,)))

        for i in range(num):
            self.auto_odometry('wheel')
            self.roll_proximity('lidar', 3, threshold=0.9)
            self.roll_closure('lidar', 2., separation=10, threshold=0.8)

            if is_gps and i in gps_ids:
                self.add_gps('gps')

            if is_dyn:
                self.truth_simulation().update_parameter('wheel', 'bias', Vector1(f_step(i)))
                # model.update_truth_parameter('wheel', 'bias', Vector1(0.1 * np.sin(0.01 * i)))

            self.step()

    def finalise(self) -> None:
        pass


class IntelPlain(IntelSim):
    def configure(self) -> None:
        super().configure()
        self.set_plain_simulation()
        self.set_name('IntelSim: Plain')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_static_parameter(
            'wheel', 'bias',
            Vector1(0.), ParameterSpecification.BIAS, index=0
        )


class IntelWithout(IntelSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('IntelSim: Without')


class IntelConstant(IntelSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('IntelSim: Constant')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_static_parameter(
            'wheel', 'bias',
            Vector1(0.), ParameterSpecification.BIAS, index=0
        )


class IntelTimely(IntelSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('IntelSim: Timely Batch')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_timely_parameter(
            'wheel', 'bias',
            Vector1(0.), ParameterSpecification.BIAS, 20, index=0
        )


class IntelSliding(IntelSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('IntelSim: Sliding')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_sliding_parameter(
            'wheel', 'bias',
            Vector1(0.), ParameterSpecification.BIAS, 20, index=0
        )


class IntelSlidingOld(IntelSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('IntelSim: Sliding (old)')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_old_sliding_parameter(
            'wheel', 'bias',
            Vector1(0.), ParameterSpecification.BIAS, 20, index=0
        )


class IntelSpatial(IntelSim):
    def configure(self) -> None:
        super().configure()
        self.set_post_simulation()
        self.set_name('IntelSim: Spatial')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_spatial_parameter(
            'wheel', 'bias', Vector1(0.),
            ParameterSpecification.BIAS, 10, index=0
        )

    def finalise(self) -> None:
        super().finalise()
        self.estimate_simulation().post_process()