import copy
import typing as tp

import matplotlib as mpl
import numpy as np
import scipy.interpolate as spi
from matplotlib import pyplot as plt
from src.framework.graph.CalibratingGraph import SubCalibratingGraph, SubCalibratingEdge
from src.framework.graph.Graph import SubGraph, SubNode, SubElement
from src.framework.graph.protocols.Visualisable import Visualisable, DrawPoint, DrawAxis, DrawEdge
from src.framework.graph.types.nodes.ParameterNode import SubParameterNode
from src.framework.graph.types.nodes.SpatialNode import SubSpatialNode
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import SubVector
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3
from src.framework.math.matrix.vector.Vector import Vector
from src.framework.optimiser.Optimiser import Optimiser, Library, Solver
from src.gui.viewer.Rgb import Rgb


class PlotData(object):
    _x: tp.List[float]
    _y: tp.List[float]

    def __init__(self):
        self._x = []
        self._y = []

    def append(self, x: float, y: float) -> None:
        self._x.append(x)
        self._y.append(y)

    def to_lists(self) -> tp.Tuple[tp.List[float], tp.List[float]]:
        return self._x, self._y



def round_up(value: float, nearest: float = 1.) -> float:
    return nearest * np.ceil(value / nearest)


def round_down(value: float, nearest: float = 1.) -> float:
    return nearest * np.floor(value / nearest)


class GraphAnalyser(object):

    # topology
    @staticmethod
    def find_domain(graph: SubGraph) -> tp.Tuple[float, float, float, float]:
        x_min: float = 0.
        x_max: float = 0.
        y_min: float = 0.
        y_max: float = 0

        type_: tp.Type[SubNode]
        for type_ in graph.get_types():
            if issubclass(type_, Visualisable):
                elements: tp.List[SubElement] = graph.get_of_type(type_)
                element: SubElement
                for element in elements:
                    if isinstance(element, DrawPoint):
                        point: Vector = element.draw_point()
                        x_min = min(x_min, point[0])
                        x_max = max(x_max, point[0])
                        y_min = min(y_min, point[1])
                        y_max = max(y_max, point[1])
        return x_min, y_min, x_max - x_min, y_max - y_min

    @classmethod
    def plot_topology(cls, graph: SubGraph):
        # ax = plt.gca()
        import time

        _, __, size_x, size_y = cls.find_domain(graph)
        fig, ax = plt.subplots(figsize=(0.2 * size_x, 0.2 * size_y))

        ti = time.time()
        for type_ in graph.get_types():
            if issubclass(type_, Visualisable):
                ti = time.time()
                elements: tp.List[SubElement] = graph.get_of_type(type_)
                element: SubElement
                for element in elements:
                    color: tp.Tuple = type_.draw_rgb()
                    if isinstance(element, DrawAxis):
                        pose: SE2 = element.draw_pose().to_se2()
                        translation: Vector2 = pose.translation()
                        t = mpl.markers.MarkerStyle(marker='4')
                        t._transform = t.get_transform().rotate_deg(np.rad2deg(pose.rotation().angle()))
                        ax.scatter(
                            (translation[0]), (translation[1]), marker=t, s=40,
                            c=[list(Rgb.invert(color))]
                        )
                    elif isinstance(element, DrawPoint):
                        point: Vector3 = element.draw_point()
                        ax.plot(point[0], point[1], color=Rgb.invert(color), marker='.')
                    elif isinstance(element, DrawEdge):
                        a, b = element.draw_nodeset()
                        ax.plot([a[0], b[0]], [a[1], b[1]], color=Rgb.invert(color), linestyle='-')
                print(f'Plotting <{type_.__name__}> = time: {time.time() - ti} s')
        ax.set_aspect('equal')
        plt.show()

    # error-slice
    @staticmethod
    def plot_error_slice(graph: SubGraph, steps: int = 50):
        assert graph.has_truth()
        assert graph.has_pre()

        pre_vector: SubVector = graph.get_pre().to_vector()
        opt_vector: SubVector = graph.to_vector()
        unit: SubVector = Vector(pre_vector.array() - opt_vector.array())

        graph: SubGraph = copy.deepcopy(graph)
        line: tp.List[float] = list(np.linspace(-2, 2, steps + 1))
        error: tp.List[float] = []
        for x in line:
            vector: SubVector = Vector(opt_vector.array() + unit.array() * x)
            graph.from_vector(vector)
            error.append(graph.compute_error())
        plt.plot(line, error)
        plt.show()

    # iterations
    @staticmethod
    def optimise_graphs(
            graphs: tp.List[SubGraph],
            optimiser: tp.Optional[Optimiser] = None,
            library: Library = Library.CHOLMOD,
            solver: Solver = Solver.GN
    ) -> tp.List[SubGraph]:
        solutions: tp.List[SubGraph] = []

        # optimiser
        optimiser: tp.Optional[Optimiser] = optimiser
        if optimiser is None:
            optimiser = Optimiser(library, solver)

        # solutions
        for i, subgraph in enumerate(graphs):
            solution: SubGraph = optimiser.instance_optimise(subgraph, verbose=True, compute_marginals=False)
            if solution is not None:
                solutions.append(solution)
        return solutions

    @staticmethod
    def plot_parameter_dynamics(graph: SubCalibratingGraph):
        assert graph.has_truth()
        for name in graph.get_parameter_names():
            parameters: tp.List[SubParameterNode] = graph.get_parameters(name)
            dim: int = parameters[0].get_dim()
            size: tp.Tuple[int, int] = dim, len(parameters)

            estimated: np.ndarray = np.zeros(size)
            truth: np.ndarray = np.zeros(size)
            timestamps: tp.List[float] = []
            for i, parameter in enumerate(parameters):
                estimated[:, i] = parameter.to_vector().array()[:, 0]
                truth[:, i] = parameter.get_truth().to_vector().array()[:, 0]
                timestamps.append(parameter.get_timestamp())
            plt.plot(timestamps, estimated[0, :], timestamps, truth[0, :])
            plt.show()

    @staticmethod
    def plot_parameter_map(graph: SubCalibratingGraph):
        assert graph.has_truth()
        for name in graph.get_parameter_names():
            parameters: tp.List[SubParameterNode] = graph.get_parameters(name)
            dim: int = parameters[0].get_dim()

            x_min, x_max, y_min, y_max = 0., 0., 0., 0.
            locations: np.ndarray = np.zeros((len(parameters), 2))
            values: np.ndarray = np.zeros((len(parameters), dim))
            for i, parameter in enumerate(parameters):
                location: np.ndarray = np.zeros((2, 1))
                nodes: tp.List[SubSpatialNode] = []

                edge: SubCalibratingEdge
                for edge in graph.get_connected_edges(parameter.get_id()):
                    node: SubSpatialNode
                    for node in edge.get_endpoints():
                        if node not in nodes:
                            nodes.append(node)
                            location += node.get_translation().array()
                location /= len(nodes)
                x_min = min(x_min, location[0, 0])
                x_max = max(x_max, location[0, 0])
                y_min = min(y_min, location[1, 0])
                y_max = max(y_max, location[1, 0])

                print(f'{location[0]}, {location[1]}')
                locations[i, :] = location[:, 0]
                values[i, :] = parameter.to_vector().array()[:, 0]
            # for i in range(dim):
            x_min = round_down(x_min, 5.)
            x_max = round_up(x_max, 5.)
            y_min = round_down(y_min, 5.)
            y_max = round_up(y_max, 5.)

            grid_x, grid_y = np.mgrid[
                x_min: x_max: complex(0, 2 * (x_max - x_min) + 1),
                y_min: y_max: complex(0, 2 * (y_max - y_min) + 1),
            ]
            grid = spi.griddata(locations, values[:, 0], (grid_x, grid_y), method='linear')
            plt.imshow(grid.T, extent=(x_min, x_max, y_min, y_max), origin='lower')
            plt.show()

    # metrics
    @staticmethod
    def plot_metrics(graph: SubGraph) -> None:
        # GraphAnalyser.plot_error_slice(graph)
        GraphAnalyser.plot_topology(graph)
        GraphAnalyser.plot_parameter_dynamics(graph)
        GraphAnalyser.plot_parameter_map(graph)

        # assert graph.has_metrics()
        # optimiser = Optimiser()
        #
        # import time
        # t = time.time()
        # subgraphs: tp.List[SubGraph] = graph.get_subgraphs()
        # suboptimised: tp.List[SubGraph] = []
        #
        # print(time.time() - t)
        # for i, subgraph in enumerate(subgraphs):
        #     print(i)
        #     if i == 9:
        #         print('9')
        #     optimised: SubGraph = optimiser.optimise(subgraph, verbose=True, compute_marginals=False)
        #     if optimised is not None:
        #         suboptimised.append(optimised)
        #
        # edge_count: tp.List[int] = []
        # error: tp.List[float] = []
        # for i, optimised in enumerate(suboptimised):
        #     error.append(optimised.compute_error())
        #     edge_count.append(i)
        # plt.plot(edge_count, error)
        # plt.show()
        # print(error)

    @classmethod
    def plot_ate(cls, graph: SubGraph):
        assert graph.has_previous()
        graphs: tp.List[SubGraph] = graph.get_subgraphs()

        data: PlotData = PlotData()
        for _, graph in enumerate(graphs):
            data.append(graph.get_timestamp(), graph.get_ate())

        plt.figure()
        # plt.ylim(0, 2 * ate[-1])
        plt.plot(*data.to_lists())
        plt.show()
