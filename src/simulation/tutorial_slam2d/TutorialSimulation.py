import pathlib
from copy import deepcopy

import numpy as np
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.framework.simulation.ConfigurationSet import ConfigurationSet


class TutorialSimulation(BiSimulation2D):

    # constructor
    def __init__(self):
        super().__init__()
        config_path: pathlib.Path = (pathlib.Path(__file__).parent / 'config.ini').resolve()
        self.set_parameters(ConfigurationSet(config_path))

    # public methods
    def _simulate(self):
        parameters = self._parameters
        assert parameters is not None
        num_nodes = parameters['num_nodes']
        step_length = parameters['step_length']
        translation_noise_x = parameters['translation_noise_x']
        translation_noise_y = parameters['translation_noise_y']
        rotation_noise_deg = parameters['rotation_noise_deg']
        proximity_probability = parameters['proximity_probability']
        proximity_separation = parameters['proximity_separation']
        reach = parameters['reach']
        closure_probability = parameters['closure_probability']
        closure_separation = parameters['closure_separation']

        info_matrix3 = Square3.from_diagonal(
            [1/translation_noise_x, 1/translation_noise_y, np.pi/(180. * rotation_noise_deg)]
        )
        true = SensorSE2()
        true.set_info_matrix(info_matrix3)
        true.add_bias('bias', SE2.from_translation_angle_elements(0.2, 0.3, 0.02))
        self.add_sensor('lidar', true, deepcopy(true))

        num: int = 5
        for _ in range(60):
            for __ in range(num):
                angle: float = np.deg2rad(np.random.choice([90, -90])) if __ == num - 1 else 0.
                motion = SE2.from_translation_angle_elements(step_length, 0, angle)
                self.add_odometry('lidar', motion)
                self.roll_proximity('lidar', proximity_separation, threshold=proximity_probability)
                self.roll_closure('lidar', reach, separation=closure_separation, threshold=closure_probability)
