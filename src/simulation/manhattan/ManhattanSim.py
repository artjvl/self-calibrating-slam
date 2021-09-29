import numpy as np
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3, Square2
from src.framework.math.matrix.vector import Vector1, Vector2
from src.framework.simulation.BiSimulation import BiSimulation
from src.framework.simulation.Path import ManhattanPath


def f_space(x, y):
    return -0.5 + 0.01 * (x + y)
    # return 0.1 * np.sin(0.1 * (x + y))


def f_step(x):
    if x > 200:
        return 0.1
    return -0.2


def f_time(x):
    return 0.1 * np.sin(0.02 * x)


class ManhattanSim(BiSimulation):

    def configure(self) -> None:
        path: ManhattanPath = ManhattanPath()
        path.set_block_size(5)
        path.set_rng(33)
        self.set_path(path)

        # seed
        self.set_sensor_seed(0)
        self.set_constraint_rng(0)

    def initialise(self) -> None:
        # sensors: wheel
        info_wheel_truth = Square3.from_diagonal([200., 200., 400.])
        info_wheel_estimate = info_wheel_truth
        self.add_sensor('whseel', SE2, info_wheel_truth, info_wheel_estimate)
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
            Vector1(1.1), ParameterSpecification.SCALE, index=1
        )

    def simulate(self) -> None:
        delta: float = 0.1
        num: int = 200  # 400

        is_gps: bool = True
        is_dyn: bool = False

        gps_num: int = 10
        gps_ids: set = set(self.get_constraint_rng().randint(1, num, size=(gps_num,)))

        for i in range(num):
            self.auto_odometry('wheel')
            self.roll_proximity('lidar', 3, threshold=0.9)
            self.roll_closure('lidar', 2., separation=10, threshold=0.6)

            if is_gps and i in gps_ids:
                self.add_gps('gps')

            if is_dyn:
                self.truth_simulation().update_parameter('wheel', 'bias', Vector1(f_step(i)))
                # model.update_truth_parameter('wheel', 'bias', Vector1(0.1 * np.sin(0.01 * i)))

            self.step()

    def finalise(self) -> None:
        pass


class ManhattanPlain(ManhattanSim):
    def configure(self) -> None:
        super().configure()
        self.set_plain_simulation()
        self.set_name('ManhattanSim: Plain')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_static_parameter(
            'wheel', 'scale',
            Vector1(1.1), ParameterSpecification.SCALE, index=1
        )


class ManhattanWithout(ManhattanSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('ManhattanSim: Without')


class ManhattanConstant(ManhattanSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('ManhattanSim: Constant')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_static_parameter(
            'wheel', 'bias',
            Vector1(1.), ParameterSpecification.SCALE, index=1
        )


class ManhattanTimely(ManhattanSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('ManhattanSim: Timely Batch')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_timely_parameter(
            'wheel', 'bias',
            Vector1(0.), ParameterSpecification.SCALE, 20, index=0
        )


class ManhattanSliding(ManhattanSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('ManhattanSim: Sliding')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_sliding_parameter(
            'wheel', 'bias',
            Vector1(0.), ParameterSpecification.SCALE, 20, index=0
        )


class ManhattanSlidingOld(ManhattanSim):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()
        self.set_name('ManhattanSim: Sliding (old)')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_old_sliding_parameter(
            'wheel', 'bias',
            Vector1(0.), ParameterSpecification.SCALE, 20, index=0
        )


class ManhattanSpatial(ManhattanSim):
    def configure(self) -> None:
        super().configure()
        self.set_post_simulation()
        self.set_name('ManhattanSim: Spatial')

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_spatial_parameter(
            'wheel', 'bias', Vector1(1.),
            ParameterSpecification.SCALE, 20, index=0
        )

    def finalise(self) -> None:
        super().finalise()
        self.estimate_simulation().post_process()