import copy
import pathlib
import pickle as pkl
import sys
import typing as tp
from datetime import datetime

import matplotlib as mpl
import numpy as np
import scipy.interpolate as spi
from matplotlib import pyplot as plt
from src.definitions import get_project_root
from src.framework.graph.CalibratingGraph import SubCalibratingGraph, SubCalibratingEdge
from src.framework.graph.protocols.Visualisable import Visualisable, DrawPoint, DrawAxis, DrawEdge
from src.framework.graph.types.nodes.ParameterNode import SubParameterNode
from src.framework.graph.types.nodes.SpatialNode import SubSpatialNode
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3
from src.framework.math.matrix.vector.Vector import Vector
from src.gui.viewer.Rgb import Rgb

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubGraph, SubNode, SubElement, SubEdge
    from src.framework.math.matrix.vector.Vector import SubSizeVector
    from src.framework.math.matrix.vector import SubVector


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


class FigureParser(object):
    _path: pathlib.Path = (get_project_root() / 'plots').resolve()

    @classmethod
    def path(cls) -> pathlib.Path:
        return cls._path

    @classmethod
    def save(
            cls,
            fig: plt.Figure,
            name: tp.Optional[str] = None
    ) -> None:
        if name is None:
            name = f"pickle_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        if not name.endswith('.pickle'):
            name += '.pickle'
        cls._path.mkdir(parents=True, exist_ok=True)
        path: pathlib.Path = (cls._path / name).resolve()
        with open(path, 'wb') as file:
            pkl.dump(fig, file)
        print(f"src/FigureParser: Figure saved as {path}")

    @classmethod
    def load(
            cls,
            name: str
    ) -> plt.Figure:
        if not name.endswith('.pickle'):
            name += '.pickle'
        path: pathlib.Path = (cls._path / name).resolve()
        assert path.is_file()
        with open(path, 'rb') as file:
            fig: plt.Figure = pkl.load(file)
        dummy = plt.figure()
        new_manager = dummy.canvas.manager
        new_manager.canvas.figure = fig
        fig.set_canvas(new_manager.canvas)
        return fig


class GraphAnalyser(object):
    _last: tp.Optional[plt.Figure]

    _error: tp.Optional[plt.Figure]
    _ate: tp.Optional[plt.Figure]
    _rpe_translation: tp.Optional[plt.Figure]
    _rpe_rotation: tp.Optional[plt.Figure]

    def __init__(self):
        self.clear()

    def clear(self) -> None:
        self._last = None

        self._error = None
        self._ate = None
        self._rpe_translation = None
        self._rpe_rotation = None

    def has_last(self) -> bool:
        return self._last is not None

    def save_last(
            self,
            name: tp.Optional[str] = None
    ) -> None:
        assert self.has_last()
        fig: plt.Figure = self._last
        FigureParser.save(fig, name)

    # topology
    @staticmethod
    def find_domain(graph: 'SubGraph') -> tp.Tuple[float, float, float, float]:
        x_min: float = 0.
        x_max: float = 0.
        y_min: float = 0.
        y_max: float = 0

        type_: tp.Type['SubNode']
        for type_ in graph.get_types():
            if issubclass(type_, Visualisable):
                elements: tp.List['SubElement'] = graph.get_of_type(type_)
                element: 'SubElement'
                for element in elements:
                    if isinstance(element, DrawPoint):
                        point: Vector = element.draw_point()
                        x_min = min(x_min, point[0])
                        x_max = max(x_max, point[0])
                        y_min = min(y_min, point[1])
                        y_max = max(y_max, point[1])
        return x_min, y_min, x_max - x_min, y_max - y_min

    def instance_plot_topology(
            self,
            graph: 'SubGraph'
    ) -> None:
        fig: plt.Figure = self.plot_topology(graph)
        self._last = fig

    @classmethod
    def plot_topology(
            cls,
            graph: 'SubGraph'
    ) -> plt.Figure:
        import time

        _, __, size_x, size_y = cls.find_domain(graph)
        fig, ax = plt.subplots(figsize=(0.2 * size_x, 0.2 * size_y))

        for type_ in graph.get_types():
            if issubclass(type_, Visualisable):
                t = time.time()
                elements: tp.List['SubElement'] = graph.get_of_type(type_)
                element: 'SubElement'
                for element in elements:
                    color: tp.Tuple = type_.draw_rgb()
                    if isinstance(element, DrawAxis):
                        pose: SE2 = element.draw_pose().to_se2()
                        translation: Vector2 = pose.translation()
                        marker = mpl.markers.MarkerStyle(marker='4')
                        marker._transform = marker.get_transform().rotate_deg(np.rad2deg(pose.rotation().angle()))
                        ax.scatter(
                            (translation[0]), (translation[1]), marker=marker, s=40,
                            c=[list(Rgb.invert(color))]
                        )
                    elif isinstance(element, DrawPoint):
                        point: Vector3 = element.draw_point()
                        ax.plot(point[0], point[1], color=Rgb.invert(color), marker='.')
                    elif isinstance(element, DrawEdge):
                        a, b = element.draw_nodeset()
                        ax.plot([a[0], b[0]], [a[1], b[1]], color=Rgb.invert(color), linestyle='-')
                print(f'Plotting <{type_.__name__}> = time: {time.time() - t} s')
        ax.set_aspect('equal')
        fig.show()
        return fig

    # error-slice
    @staticmethod
    def plot_error_slice(graph: 'SubGraph', steps: int = 50):
        assert graph.has_truth()
        assert graph.has_pre()

        pre_vector: 'SubVector' = graph.get_pre().to_vector()
        opt_vector: 'SubVector' = graph.to_vector()
        unit: 'SubVector' = Vector(pre_vector.array() - opt_vector.array())

        graph: 'SubGraph' = copy.deepcopy(graph)
        line: tp.List[float] = list(np.linspace(-2, 2, steps + 1))
        error: tp.List[float] = []
        for x in line:
            vector: 'SubVector' = Vector(opt_vector.array() + unit.array() * x)
            graph.from_vector(vector)
            error.append(graph.compute_error())
        plt.plot(line, error)
        plt.show()

    # parameters
    @staticmethod
    def plot_parameter(
            graph: SubCalibratingGraph,
            name: str
    ) -> None:
        assert graph.has_name(name)
        parameters: tp.List[SubParameterNode] = graph.get_of_name(name)
        assert len(parameters) > 1

        print(f"Plotting parameter '{name}' for {graph.to_unique()}..")

        dim: int = parameters[0].get_dim()
        data: tp.List[PlotData] = [PlotData() for _ in range(dim)]
        for parameter in parameters:
            vector: 'SubVector' = parameter.to_vector()
            timestamp: float = parameter.get_timestamp()
            for i in range(dim):
                data[i].append(timestamp, vector[i])

        fig, axes = plt.subplots(dim, 1)
        for i, ax in enumerate(np.array(axes).flatten()):
            ax.plot(*(data[i].to_lists()))
        fig.show()

    @staticmethod
    def plot_parameter_dynamics(
            graph: SubCalibratingGraph,
            name: str
    ) -> None:
        assert graph.has_name(name)
        assert graph.has_previous()

        print(f"Plotting parameter dynamics of '{name}' for {graph.to_unique()}..")

        dim: int = graph.get_type_of_name(name).get_dim()
        data: tp.List[PlotData] = [PlotData() for _ in range(dim)]

        subgraphs: tp.List[SubCalibratingGraph] = graph.get_subgraphs()
        size: int = len(subgraphs)

        for i, subgraph in enumerate(subgraphs):
            parameters: tp.List[SubParameterNode] = subgraph.get_of_name(name)
            assert len(parameters) == 1
            parameter: SubParameterNode = parameters[0]

            vector: 'SubVector' = parameter.to_vector()
            timestamp: float = subgraph.get_timestamp()
            for i in range(dim):
                data[i].append(timestamp, vector[i])

            sys.__stdout__.write(f'\r{100 * i / size:.2f}%')
            sys.__stdout__.flush()
        sys.__stdout__.write(f'\rDone!\n')
        sys.__stdout__.flush()

        fig, axes = plt.subplots(dim, 1)
        for i, ax in enumerate(np.array(axes).flatten()):
            ax.plot(*(data[i].to_lists()))
        fig.show()

    @staticmethod
    def plot_parameter_map(graph: SubCalibratingGraph):
        assert graph.has_truth()
        for name in graph.get_parameter_names():
            parameters: tp.List[SubParameterNode] = graph.get_of_name(name)
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

    # covariance
    def instance_plot_edge_estimate_variance(
            self,
            graph: 'SubGraph',
            name: str,
            window: int = 50
    ) -> None:
        fig: plt.Figure = self.plot_edge_estimate_variance(graph, name, window)
        self._last = fig

    @staticmethod
    def plot_edge_estimate_variance(
            graph: 'SubGraph',
            name: str,
            window: int = 50
    ) -> plt.Figure:
        assert name in graph.get_edge_names()

        print(f"Plotting edge variance of '{name}' for {graph.to_unique()}..")

        dim: int = graph.get_type_of_name(name).get_dim()
        data: tp.List[PlotData] = [PlotData() for _ in range(dim)]

        left: int = int(np.floor(window / 2))
        right: int = window - left

        edges: tp.List['SubEdge'] = graph.get_of_name(name)
        size = len(edges)
        for i, edge in enumerate(edges):
            edge_window: tp.List[edges] = edges[np.maximum(0, i - left + 1): i + right + 1]
            error_vectors: tp.List['SubVector'] = [edge.get_error_vector() for edge in edge_window]

            for d in range(dim):
                errors: tp.List[float] = [error_vector[d] for error_vector in error_vectors]
                data[d].append(i, float(np.var(errors)))

            sys.__stdout__.write(f'\r{100 * i / size:.2f}%')
            sys.__stdout__.flush()
        sys.__stdout__.write(f'\rDone!\n')
        sys.__stdout__.flush()

        fig, axes = plt.subplots(dim, 1)
        for i, ax in enumerate(np.array(axes).flatten()):
            ax.plot(*(data[i].to_lists()))
        fig.show()
        return fig

    def instance_plot_edge_variance(
            self,
            graph: 'SubGraph',
            name: str
    ) -> None:
        fig: plt.Figure = self.plot_edge_variance(graph, name)
        self._last = fig

    @staticmethod
    def plot_edge_variance(
            graph: 'SubGraph',
            name: str
    ) -> plt.Figure:
        assert name in graph.get_edge_names()

        print(f"Plotting edge variance of '{name}' for {graph.to_unique()}..")

        dim: int = graph.get_type_of_name(name).get_dim()
        data: tp.List[PlotData] = [PlotData() for _ in range(dim)]

        edges: tp.List['SubEdge'] = graph.get_of_name(name)
        size = len(edges)
        for i, edge in enumerate(edges):
            cov_diagonal: 'SubSizeVector' = edge.get_cov_matrix().diagonal()
            for d in range(dim):
                data[d].append(i, cov_diagonal[d])

            sys.__stdout__.write(f'\r{100 * i / size:.2f}%')
            sys.__stdout__.flush()
        sys.__stdout__.write(f'\rDone!\n')
        sys.__stdout__.flush()

        fig, axes = plt.subplots(dim, 1)
        for i, ax in enumerate(np.array(axes).flatten()):
            ax.plot(*(data[i].to_lists()))
        fig.show()
        return fig

    # metrics
    def instance_plot_error(
            self,
            graph: 'SubGraph'
    ):
        fig: plt.Figure = self.plot_error(graph, self._error)
        self._error = fig
        self._last = fig

    @classmethod
    def plot_error(
            cls,
            graph: 'SubGraph',
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        assert graph.has_previous()

        print(f"Plotting error for {graph.to_unique()}..")

        if fig is None:
            fig, ax = plt.subplots()
            ax.set_title('Error')

        subgraphs: tp.List['SubGraph'] = graph.get_subgraphs()
        size: int = len(subgraphs)

        data: PlotData = PlotData()
        for i, subgraph in enumerate(subgraphs):
            data.append(subgraph.get_timestamp(), subgraph.get_error())

            sys.__stdout__.write(f'\r{100 * i / size:.2f}%')
            sys.__stdout__.flush()
        sys.__stdout__.write(f'\rDone!\n')
        sys.__stdout__.flush()

        ax: plt.Axes = fig.axes[0]
        ax.plot(*data.to_lists())
        fig.show()
        return fig

    def instance_plot_ate(
            self,
            graph: 'SubGraph'
    ):
        fig: plt.Figure = self.plot_ate(graph, self._ate)
        self._ate = fig
        self._last = fig

    @classmethod
    def plot_ate(
            cls,
            graph: 'SubGraph',
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        assert graph.has_previous()

        print(f"Plotting ATE for {graph.to_unique()}..")

        if fig is None:
            fig, ax = plt.subplots()
            ax.set_title('ATE')

        subgraphs: tp.List['SubGraph'] = graph.get_subgraphs()
        size: int = len(subgraphs)

        data: PlotData = PlotData()
        for i, subgraph in enumerate(subgraphs):
            data.append(subgraph.get_timestamp(), subgraph.get_ate())

            sys.__stdout__.write(f'\r{100 * i / size:.2f}%')
            sys.__stdout__.flush()
        sys.__stdout__.write(f'\rDone!\n')
        sys.__stdout__.flush()

        ax: plt.Axes = fig.axes[0]
        ax.plot(*data.to_lists())
        fig.show()
        return fig

    def instance_plot_rpe_translation(
            self,
            graph: 'SubGraph'
    ):
        fig: plt.Figure = self.plot_rpe_translation(graph, self._rpe_translation)
        self._rpe_translation = fig
        self._last = fig

    @classmethod
    def plot_rpe_translation(
            cls,
            graph: 'SubGraph',
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        assert graph.has_previous()

        print(f"Plotting RPE (translation) for {graph.to_unique()}..")

        if fig is None:
            fig, ax = plt.subplots()
            ax.set_title('RPE (translation)')

        subgraphs: tp.List['SubGraph'] = graph.get_subgraphs()
        size: int = len(subgraphs)

        data: PlotData = PlotData()
        for i, subgraph in enumerate(subgraphs):
            data.append(subgraph.get_timestamp(), subgraph.get_rpe_translation())

            sys.__stdout__.write(f'\r{100 * i / size:.2f}%')
            sys.__stdout__.flush()
        sys.__stdout__.write(f'\rDone!\n')
        sys.__stdout__.flush()

        ax: plt.Axes = fig.axes[0]
        ax.plot(*data.to_lists())
        fig.show()
        return fig

    def instance_plot_rpe_rotation(
            self,
            graph: 'SubGraph'
    ):
        fig: plt.Figure = self.plot_rpe_rotation(graph, self._rpe_rotation)
        self._rpe_rotation = fig
        self._last = fig

    @classmethod
    def plot_rpe_rotation(
            cls,
            graph: 'SubGraph',
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        assert graph.has_previous()

        print(f"Plotting RPE (rotation) for {graph.to_unique()}..")

        if fig is None:
            fig, ax = plt.subplots()
            ax.set_title('RPE (rotation)')

        subgraphs: tp.List['SubGraph'] = graph.get_subgraphs()
        size: int = len(subgraphs)

        data: PlotData = PlotData()
        for i, subgraph in enumerate(subgraphs):
            data.append(subgraph.get_timestamp(), subgraph.get_rpe_rotation())

            sys.__stdout__.write(f'\r{100 * i / size:.2f}%')
            sys.__stdout__.flush()
        sys.__stdout__.write(f'\rDone!\n')
        sys.__stdout__.flush()

        ax: plt.Axes = fig.axes[0]
        ax.plot(*data.to_lists())
        fig.show()
        return fig
