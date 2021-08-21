import typing as tp
from abc import ABC

import numpy as np
from src.framework.math.lie.transformation import SE2
from src.framework.simulation.BiSimulation2D import BiSimulation2D

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.vector import Vector2


class ManhattanSimulation2D(BiSimulation2D, ABC):
    _block_size: int
    _step_size: float
    _domain: float
    _step_count: int

    def __init__(self):
        super().__init__()
        self._block_size = 4
        self._step_size = 1.
        self._domain = 50.
        self._step_count = 0

    def reset(self) -> None:
        super().reset()
        self._step_count = 0

    def set_block_size(self, block_size: int) -> None:
        self._block_size = block_size

    def set_step_size(self, step_size: float) -> None:
        self._step_size = step_size

    def set_domain(self, domain: float) -> None:
        self._domain = domain

    def auto_odometry(
            self,
            sensor_name: str
    ) -> None:
        self._step_count += 1

        angle: float = 0.
        if self._step_count == self._block_size:
            angle = self.generate_new_angle()
            self._step_count = 0

        pose: SE2 = SE2.from_translation_angle_elements(self._step_size, 0., angle)
        self.add_odometry(sensor_name, pose)

    def generate_new_angle(self) -> float:
        angle = np.deg2rad(self.get_rng().choice([90., -90.]))
        translation: Vector2 = self.get_current_pose().translation()
        if np.max(np.abs(translation.array())) > self._domain - self._step_count:
            proposed: SE2 = self.get_current_pose() * \
                            SE2.from_translation_angle_elements(self._step_size, 0., angle) * \
                            SE2.from_translation_angle_elements(self._step_count * self._step_size, 0., 0.)
            if not self.is_in_domain(proposed):
                angle += np.pi
        return angle

    def is_in_domain(self, pose: SE2) -> bool:
        translation: 'Vector2' = pose.translation()
        return np.max(np.abs(translation.array())) <= self._domain
