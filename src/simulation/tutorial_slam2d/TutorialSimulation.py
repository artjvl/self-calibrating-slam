import pathlib

import numpy as np
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.simulation.ConfigurationSet import ConfigurationSet
from src.framework.simulation.simulations.ManhattanSimulation2D import ManhattanSimulation2D


class TutorialSimulation(ManhattanSimulation2D):

    # constructor
    def __init__(self):
        super().__init__()
        config_path: pathlib.Path = (pathlib.Path(__file__).parent / 'config.ini').resolve()
        self.set_config(ConfigurationSet(config_path))

        info_matrix3 = Square3.from_diagonal(
            [1/self._config['translation_noise_x'],
             1/self._config['translation_noise_y'],
             np.pi/(180. * self._config['rotation_noise_deg'])]
        )
        self.add_sensor('lidar', SE2, info_matrix3, info_matrix3)
        self.add_truth_parameter(
            'lidar', 'bias',
            SE2.from_translation_angle_elements(0.2, 0.3, 0.02), ParameterSpecification.BIAS
        )
        self.set_step_size(self._config['step_length'])

    # public methods
    def loop(self):

        num: int = 5
        for _ in range(60):
            for __ in range(num):
                angle: float = np.deg2rad(np.random.choice([90, -90])) if __ == num - 1 else 0.
                motion = SE2.from_translation_angle_elements(self._config['step_length'], 0, angle)
                self.add_odometry('lidar', motion)
                self.roll_proximity('lidar', self._config['proximity_separation'], threshold=self._config['proximity_probability'])
                self.roll_closure('lidar', self._config['reach'], separation=self._config['closure_separation'], threshold=self._config['closure_probability'])
