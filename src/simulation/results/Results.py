import pathlib
import typing as tp
from abc import ABC, abstractmethod

from src.definitions import get_project_root
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3, Square2
from src.framework.math.matrix.vector import Vector2
from src.framework.simulation.BiSimulation import BiSimulation
from src.framework.simulation.Path import ManhattanPath, InputPath

if tp.TYPE_CHECKING:
    from src.framework.optimiser.Optimiser import Optimiser

SubResults = tp.TypeVar('SubResults', bound='Results')


class Results(BiSimulation, ABC):
    _num_steps: tp.Optional[int]
    def __init__(
            self,
            name: tp.Optional[str] = None,
            optimiser: tp.Optional['Optimiser'] = None
    ):
        super().__init__(name=name, optimiser=optimiser)
        self._num_steps = None

    def set_steps(self, num_steps: int) -> 'SubResults':
        self._num_steps = num_steps
        return self

    def configure(self) -> None:
        self.set_config(2)  # CHANGE DEFAULT CONFIG HERE
        self.set_sensor_seed(0)
        self.set_constraint_rng(0)

    def set_intel(self) -> 'SubResults':
        path: InputPath = InputPath()
        root: pathlib.Path = get_project_root()
        path.set_input_file((root / 'graphs/solution_INTEL_g2o.g2o').resolve())
        self.set_path(path)
        return self

    def set_manhattan(self) -> 'SubResults':
        path: ManhattanPath = ManhattanPath()
        path.set_block_size(5)  # 5
        path.set_rng(33)  # 33
        self.set_path(path)
        return self

    def initialise(self) -> None:
        # sensors: wheel
        info_wheel_truth = Square3.from_diagonal([400., 400., 400.])
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

    def simulate(self) -> None:
        assert self._num_steps is not None
        gps_num: int = 10  # 10
        gps_ids: set = set(self.get_constraint_rng().randint(1, self._num_steps, size=(gps_num,)))

        costs: tp.List[float] = []

        for i in range(self._num_steps):
            self.auto_odometry('wheel')
            self.roll_proximity('lidar', 3, threshold=0.9)
            self.roll_closure('lidar', 2., separation=10, threshold=0.6)
            if i in gps_ids:
                self.add_gps('gps')

            self.loop(i)

            self.step()
            cost = self.estimate_simulation().graph().get_error()
            costs.append(cost)

    @abstractmethod
    def loop(self, iteration: int) -> None:
        pass
