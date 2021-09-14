from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3, Square2
from src.framework.math.matrix.vector import Vector3, Vector2
from src.framework.simulation.Model2D import PostModel2D
from src.framework.simulation.Model2D import SubModel2D
from src.framework.simulation.Simulation import ManhattanSimulation2D


class ManhattanTest(ManhattanSimulation2D):

    def configure(self) -> None:
        self.set_block_size(6)  # 6

        model: 'PostModel2D' = self.model()
        model.set_path_rng(33)  # 4, 33
        model.set_constraint_rng(0)
        model.set_sensor_seed(0)

        info_diagonal = Vector3([900., 1225., 1600.])
        info_matrix3 = Square3.from_diagonal(info_diagonal.to_list())

        # wheel
        model.add_sensor('wheel', SE2, info_matrix3, info_matrix3)

        # lidar
        model.add_sensor('lidar', SE2, info_matrix3, info_matrix3)

        # gps
        info_matrix2 = Square2.from_diagonal([800., 600.])
        model.add_sensor('gps', Vector2, info_matrix2, info_matrix2)

        model.add_variance_analyser('wheel', 40)

    def simulate(self) -> None:
        model: 'SubModel2D' = self.model()

        for i in range(300):  # 400
            self.auto_odometry('wheel')

            if i == 100:
                model.get_truth_sensor('wheel').set_info_matrix(Square3.from_diagonal([90., 122.5, 160.]))
            if i == 200:
                model.get_truth_sensor('wheel').set_info_matrix(Square3.from_diagonal([900., 1225., 1600.]))

            model.roll_proximity('lidar', 3, threshold=0.8)
            model.roll_closure('lidar', 2., separation=10, threshold=0.2)

    def finalise(self) -> None:
        self.model().post_process()


model: 'SubModel2D' = PostModel2D()
manhattan_test_post = ManhattanTest('ManhattanTest: Post', model)
