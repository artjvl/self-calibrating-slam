import pathlib
from copy import deepcopy

import numpy as np

from src.framework.graph.types.scslam2d.nodes.information import InformationNodeFull3
from src.framework.graph.types.scslam2d.nodes.parameter import ParameterNodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector3, Vector6
from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.framework.simulation.ParameterSet import ParameterSet
from src.framework.simulation.sensors.SensorSE2 import SensorSE2


class TutorialSimulation(BiSimulation2D):

    # constructor
    def __init__(self):
        super().__init__()
        config_path: pathlib.Path = (pathlib.Path(__file__).parent / 'config.ini').resolve()
        self.set_parameters(ParameterSet(config_path))

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

        info = InformationNodeFull3()
        info.set_value(
            Vector6(
                1/translation_noise_x,
                0.,
                0.,
                1/translation_noise_y,
                0.,
                1/np.deg2rad(rotation_noise_deg)
            )
        )
        par = ParameterNodeSE2()
        par.set_value(SE2.from_translation_angle_elements(0.2, 0.3, 0.02))
        par.set_as_bias()
        true = SensorSE2()
        true.add_parameter(par)
        true.add_information(info)
        self.add_sensor('lidar', true, deepcopy(true))

        angle: float = np.deg2rad(0)
        for _ in range(60):
            for __ in range(int(parameters['step_count'])):
                motion = SE2.from_elements(step_length, 0, angle)
                angle = np.deg2rad(0)
                self.add_odometry(motion, 'lidar')
                self.add_proximity(proximity_separation, 'lidar', threshold=proximity_probability)
                self.add_closure(reach, 'lidar', separation=closure_separation, threshold=closure_probability)
            angle = np.deg2rad(np.random.choice([90, -90]))

