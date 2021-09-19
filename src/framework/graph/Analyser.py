import pathlib
import pickle as pkl
import sys
import typing as tp
from abc import abstractmethod
from datetime import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from src.definitions import get_project_root
from src.framework.graph.protocols.Visualisable import Visualisable, DrawPoint, DrawAxis, DrawEdge
from src.framework.math.matrix.vector.Vector import Vector
from src.gui.viewer.Rgb import Rgb

if tp.TYPE_CHECKING:
    from src.framework.graph.CalibratingGraph import SubCalibratingGraph
    from src.framework.graph.Graph import SubGraph, SubNode, SubElement, SubEdge
    from src.framework.graph.types.nodes.ParameterNode import SubParameterNode
    from src.framework.math.lie.transformation import SE2
    from src.framework.math.matrix.vector.Vector import SubSizeVector
    from src.framework.math.matrix.vector import SubVector, Vector2, Vector3


class SubgraphSet(object):
    _subgraphs: np.ndarray

    def __init__(self, graphs: tp.List['SubGraph']):
        self._subgraphs = np.array([graphs[0].get_subgraphs()])
        for graph in graphs[1:]:
            subgraphs: tp.List['SubGraph'] = graph.get_subgraphs()
            assert len(subgraphs) == self._subgraphs.shape[1]
            self._subgraphs = np.vstack([self._subgraphs, subgraphs])

    def graphs(self, graph_index) -> tp.List['SubGraph']:
        return list(self._subgraphs[graph_index, :])

    def subgraphs(self, subgraph_index) -> tp.List['SubGraph']:
        return list(self._subgraphs[:, subgraph_index])


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


def update_print(text: str) -> None:
    sys.__stdout__.write(f'\r{text}')
    sys.__stdout__.flush()


class AnalyserTopology(object):

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

    @classmethod
    def plot(
            cls,
            graph: 'SubGraph'
    ) -> plt.Figure:
        import time

        _, __, size_x, size_y = cls.find_domain(graph)
        fig, ax = plt.subplots(figsize=(6, 6))
        # fig, ax = plt.subplots(figsize=(0.2 * size_x, 0.2 * size_y))

        for type_ in graph.get_types():
            if issubclass(type_, Visualisable):
                t = time.time()
                elements: tp.List['SubElement'] = graph.get_of_type(type_)
                element: 'SubElement'
                for element in elements:
                    color: tp.Tuple = type_.draw_rgb()
                    if isinstance(element, DrawAxis):
                        pose: 'SE2' = element.draw_pose().to_se2()
                        translation: 'Vector2' = pose.translation()
                        marker = mpl.markers.MarkerStyle(marker='4')
                        marker._transform = marker.get_transform().rotate_deg(np.rad2deg(pose.rotation().angle()))
                        ax.scatter(
                            (translation[0]), (translation[1]), marker=marker, s=40,
                            c=[list(Rgb.invert(color))]
                        )
                    elif isinstance(element, DrawPoint):
                        point: 'Vector3' = element.draw_point()
                        ax.plot(point[0], point[1], color=Rgb.invert(color), marker='.')
                    elif isinstance(element, DrawEdge):
                        a, b = element.draw_nodeset()
                        ax.plot([a[0], b[0]], [a[1], b[1]], color=Rgb.invert(color), linestyle='-')
                print(f'Plotting <{type_.__name__}> = time: {time.time() - t} s')
        ax.set_aspect('equal')
        fig.show()
        return fig


class AnalyserMetric(object):
    _fig: plt.Figure
    _attr: str

    def __init__(self):
        self._fig = self.create_fig()

    @staticmethod
    @abstractmethod
    def create_fig() -> plt.Figure:
        pass

    @staticmethod
    def is_eligible(graph: 'SubGraph') -> bool:
        return graph.has_truth() and graph.has_previous()

    @classmethod
    def is_group_eligible(cls, graphs: tp.List['SubGraph']) -> bool:
        return all(cls.is_eligible(graph) for graph in graphs)

    @classmethod
    def get_metric(cls, graph: 'SubGraph') -> float:
        return getattr(graph, cls._attr)()

    def clear(self) -> None:
        self._fig = self.create_fig()

    def plot(self, graph: 'SubGraph') -> plt.Figure:
        assert self.is_eligible(graph)

        subgraphs: tp.List['SubGraph'] = graph.get_subgraphs()
        size: int = len(subgraphs)

        timestamps: tp.List[float] = []
        metrics: tp.List[float] = []
        for i, subgraph in enumerate(subgraphs):
            timestamps.append(subgraph.get_timestamp())
            metrics.append(self.get_metric(subgraph))

            update_print(f'\r{100 * i / size:.2f}%')
        update_print('\rDone!\n')

        ax: plt.Axes = self._fig.axes[0]
        ax.plot(timestamps, metrics)
        self._fig.show()
        return self._fig

    def plot_group(self, graphs: tp.List['SubGraph']) -> plt.Figure:
        assert self.is_group_eligible(graphs)

        subgraph_set: SubgraphSet = SubgraphSet(graphs)
        first: tp.List['SubGraph'] = subgraph_set.graphs(0)
        size: int = len(first)

        timestamps: tp.List[float] = []
        means: tp.List[float] = []
        stds: tp.List[float] = []
        for i, graph in enumerate(first):
            timestamps.append(graph.get_timestamp())
            subgraphs: tp.List['SubGraph'] = subgraph_set.subgraphs(i)
            metrics: tp.List[float] = [self.get_metric(subgraph) for subgraph in subgraphs]

            means.append(float(np.mean(metrics)))
            stds.append(float(np.std(metrics)))

            update_print(f'\r{100 * i / size:.2f}%')
        update_print('\rDone!\n')

        means_array: np.ndarray = np.array(means)
        stds_array: np.ndarray = np.array(stds)

        ax: plt.Axes = self._fig.axes[0]
        ax.plot(timestamps, means_array)
        ax.fill_between(timestamps, means_array - stds_array, means_array + stds_array, alpha=0.2)
        self._fig.show()
        return self._fig


class AnalyserATE(AnalyserMetric):
    _attr = 'get_ate'

    @staticmethod
    def create_fig() -> plt.Figure:
        fig: plt.Figure
        ax: plt.Axes
        fig, ax = plt.subplots()
        ax.set_title('ATE - time')
        ax.set_xlabel(r'Time [s]')
        ax.set_ylabel(r'ATE [m]')
        return fig


class AnalyserRPET(AnalyserMetric):
    _attr = 'get_rpe_translation'

    @staticmethod
    def create_fig() -> plt.Figure:
        fig: plt.Figure
        ax: plt.Axes
        fig, ax = plt.subplots()
        ax.set_title('RPE (translation) - time')
        ax.set_xlabel(r'Time [s]')
        ax.set_ylabel(r'RPE (translation) [m]')
        return fig


class AnalyserRPER(AnalyserMetric):
    _attr = 'get_rpe_rotation'

    @staticmethod
    def create_fig() -> plt.Figure:
        fig: plt.Figure
        ax: plt.Axes
        fig, ax = plt.subplots()
        ax.set_title('RPE (rotation) - time')
        ax.set_xlabel(r'Time [s]')
        ax.set_ylabel(r'RPE (rotation) [rad]')
        return fig


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


class AnalyserParameterValues(object):

    @staticmethod
    def is_eligible(graph: 'SubCalibratingGraph', name: str) -> bool:
        return name in graph.get_parameter_names() and len(graph.get_of_name(name)) > 1

    @staticmethod
    def is_group_eligible(graphs: tp.List['SubGraph'], name: str) -> bool:
        return all(graph.has_name(name) for graph in graphs)

    @classmethod
    def plot(cls, graph: 'SubCalibratingGraph', name: str) -> plt.Figure:
        assert cls.is_eligible(graph, name)

        parameters: tp.List['SubParameterNode'] = graph.get_of_name(name)
        size: int = len(parameters)
        dim: int = parameters[0].get_dim()

        timestamps: tp.List[float] = []
        data: np.ndarray = np.zeros((dim, size))
        for i, parameter in enumerate(parameters):
            vector: 'SubSizeVector' = parameter.to_vector()
            timestamps.append(parameter.get_timestamp())
            for j in range(dim):
                data[j, i] = vector[j]

        fig, axes = plt.subplots(dim, 1)
        for i, ax in enumerate(np.array(axes).flatten()):
            ax.plot(timestamps, data[i, :])
        fig.show()
        return fig

    @classmethod
    def plot_group(cls, graphs: tp.List['SubCalibratingGraph'], name: str) -> plt.Figure:
        assert cls.is_group_eligible(graphs, name)

        first: 'SubCalibratingGraph' = graphs[0]
        parameters: tp.List['SubParameterNode'] = first.get_of_name(name)
        if len(parameters) > 1:
            return cls.plot_group_plural(graphs, name)
        return cls.plot_group_singular(graphs, name)

    @classmethod
    def plot_group_plural(cls, graphs: tp.List['SubCalibratingGraph'], name: str) -> plt.Figure:
        assert cls.is_group_eligible(graphs, name)

        parameter_set: np.ndarray = np.array([graphs[0].get_of_name(name)])
        for graph in graphs[1:]:
            parameters: tp.List['SubParameterNode'] = graph.get_of_name(name)
            assert len(parameters) == parameter_set.shape[1]
            parameter_set = np.vstack([parameter_set, parameters])

        first: tp.List['SubParameterNode'] = parameter_set[0, :]
        dim: int = first[0].get_dim()
        size: int = len(first)

        timestamps: tp.List[float] = []
        mean_set: np.ndarray = np.zeros((dim, size))
        std_set: np.ndarray = np.zeros((dim, size))

        for i, parameter in enumerate(first):
            timestamps.append(parameter.get_timestamp())
            vectors: tp.List['SubSizeVector'] = [parameter.to_vector() for parameter in parameter_set[:, i]]
            for j in range(dim):
                values: tp.List[float] = [vector[j] for vector in vectors]
                mean_set[j, i] = float(np.mean(values))
                std_set[j, i] = float(np.std(values))

            update_print(f'\r{100 * i / size:.2f}%')
        update_print('\rDone!\n')

        fig: plt.Figure = cls.create_fig(name, dim)
        for i, ax in enumerate(fig.axes):
            means = mean_set[i, :]
            stds = std_set[i, :]
            ax.plot(timestamps, means)
            ax.fill_between(timestamps, means - stds, means + stds, alpha=0.2)
        fig.show()
        return fig

    @staticmethod
    def create_fig(name: str, dim: int) -> plt.Figure:
        fig: plt.Figure
        fig, _ = plt.subplots(dim, 1)
        fig.suptitle(f"Parameters '{name}'")
        for ax in fig.axes:
            ax.set_xlabel(r'Time [-]')
            ax.set_ylabel(r'Value [-]')
        return fig

    @classmethod
    def plot_group_singular(cls, graphs: tp.List['SubCalibratingGraph'], name: str) -> plt.Figure:
        assert cls.is_group_eligible(graphs, name)

        parameters: tp.List['SubParameterNode'] = [graph.get_of_name(name)[0] for graph in graphs]
        dim: int = parameters[0].get_dim()
        size: int = len(parameters)

        values = np.zeros((dim, size))
        for i, parameter in enumerate(parameters):
            vector: 'SubSizeVector' = parameter.to_vector()
            for j in range(dim):
                values[j, i] = vector[j]

        fig = cls.create_histo_fig(name, dim)
        for i, ax in enumerate(fig.axes):
            cls.plot_histo_distribution(ax, values[i, :])
        fig.show()
        return fig

    @staticmethod
    def create_histo_fig(name: str, dim: int) -> plt.Figure:
        fig: plt.Figure
        fig, _ = plt.subplots(dim, 1)
        fig.suptitle(f"PDF of parameter '{name}'")
        for ax in fig.axes:
            ax.set_xlabel(r'Value [-]')
            ax.set_ylabel(r'Probability [-]')
        return fig

    @staticmethod
    def plot_histo_distribution(ax: plt.Axes, values: tp.List[float]) -> None:
        from scipy.stats import norm

        # plot normal distribution
        mean: float = float(np.mean(values))
        std: float = float(np.std(values))
        x = np.linspace(mean - 3*std, mean + 3*std, 100)
        normal: np.ndarray = norm.pdf(x, mean, std)
        # ax.plot(x, normal, color='b')
        ax.fill_between(x, normal, color='b', alpha=0.2)

        # plot histogram
        counts, bins = np.histogram(values, bins='auto')
        factor: float = max(normal) / max(counts)
        ax.hist(bins[:-1], bins, weights=counts * factor, color='b', alpha=0.2)
        for value in values:
            ax.axvline(x=value)


class AnalyserParameterDynamics(object):
    @staticmethod
    def is_eligible(graph: 'SubCalibratingGraph', name: str) -> bool:
        return name in graph.get_parameter_names() and len(graph.get_of_name(name)) == 1

    @classmethod
    def is_group_eligible(cls, graphs: tp.List['SubGraph'], name: str) -> bool:
        return all(cls.is_eligible(graph, name) for graph in graphs)

    @classmethod
    def plot(cls, graph: 'SubCalibratingGraph', name: str) -> plt.Figure:
        assert cls.is_eligible(graph, name)
        subgraphs: tp.List['SubCalibratingGraph'] = graph.get_subgraphs()
        parameters: tp.List['SubParameterNode'] = [graph.get_of_name(name)[0] for graph in subgraphs]

        size: int = len(parameters)
        dim: int = parameters[0].get_dim()

        timestamps: tp.List[float] = []
        data: np.ndarray = np.zeros((dim, size))
        for i, graph in enumerate(subgraphs):
            parameter: 'SubParameterNode' = parameters[i]
            vector: 'SubSizeVector' = parameter.to_vector()
            timestamps.append(graph.get_timestamp())
            for j in range(dim):
                data[j, i] = vector[j]

        fig, axes = plt.subplots(dim, 1)
        for i, ax in enumerate(np.array(axes).flatten()):
            ax.plot(timestamps, data[i, :])
        fig.show()
        return fig

    @classmethod
    def plot_group(cls, graphs: tp.List['SubCalibratingGraph'], name: str) -> plt.Figure:
        assert cls.is_group_eligible(graphs, name)

        first: tp.List['SubCalibratingGraph'] = graphs[0].get_subgraphs()
        parameter_set: np.ndarray = np.array([[graph.get_of_name(name)[0] for graph in first]])
        for graph in graphs[1:]:
            parameters: tp.List['SubParameterNode'] = [graph.get_of_name(name)[0] for graph in graph.get_subgraphs()]
            assert len(parameters) == parameter_set.shape[1]
            parameter_set = np.vstack([parameter_set, parameters])

        first_parameters: tp.List['SubParameterNode'] = parameter_set[0, :]
        dim: int = first_parameters[0].get_dim()
        size: int = len(first_parameters)

        timestamps: tp.List[float] = []
        mean_set: np.ndarray = np.zeros((dim, size))
        std_set: np.ndarray = np.zeros((dim, size))

        for i, graph in enumerate(first):
            timestamps.append(graph.get_timestamp())
            vectors: tp.List['SubSizeVector'] = [parameter.to_vector() for parameter in parameter_set[:, i]]
            for j in range(dim):
                values: tp.List[float] = [vector[j] for vector in vectors]
                mean_set[j, i] = float(np.mean(values))
                std_set[j, i] = float(np.std(values))

            update_print(f'\r{100 * i / size:.2f}%')
        update_print('\rDone!\n')

        fig: plt.Figure = cls.create_fig(name, dim)
        for i, ax in enumerate(fig.axes):
            means = mean_set[i, :]
            stds = std_set[i, :]
            ax.plot(timestamps, means)
            ax.fill_between(timestamps, means - stds, means + stds, alpha=0.2)
        fig.show()
        return fig

    @staticmethod
    def create_fig(name: str, dim: int) -> plt.Figure:
        fig: plt.Figure
        fig, _ = plt.subplots(dim, 1)
        fig.suptitle(f"Parameter dynamics of '{name}'")
        for ax in fig.axes:
            ax.set_xlabel(r'Time [s]')
            ax.set_ylabel(r'Value [-]')
        return fig


class AnalyserVariance(object):

    @staticmethod
    def is_eligible(graph: 'SubGraph', name: str) -> bool:
        return name in graph.get_edge_names()

    @classmethod
    def is_group_eligible(cls, graphs: tp.List['SubGraph'], name: str) -> bool:
        return all(cls.is_eligible(graph, name) for graph in graphs)

    @staticmethod
    def timestamps(edges: tp.List['SubEdge']) -> tp.List[float]:
        return [edge.get_timestamp() for edge in edges]

    @staticmethod
    def estimate_variances(edges: tp.List['SubEdge'], window: int) -> np.ndarray:
        size: int = len(edges)
        dim: int = edges[0].get_dim()

        left: int = int(np.floor(window / 2))
        right: int = window - left

        data: np.ndarray = np.zeros((dim, size))
        for i, edge in enumerate(edges):
            edge_window: tp.List[edges] = edges[np.maximum(0, i - left + 1): i + right + 1]
            error_vectors: tp.List['SubVector'] = [edge.get_error_vector() for edge in edge_window]
            for j in range(dim):
                errors: tp.List[float] = [error_vector[j] for error_vector in error_vectors]
                data[j, i] = float(np.var(errors))
        return data

    @classmethod
    def plot_estimate_variance(
            cls,
            graph: 'SubGraph',
            name: str,
            window: int = 50
    ) -> plt.Figure:
        assert cls.is_eligible(graph, name)

        edges: tp.List['SubEdge'] = graph.get_of_name(name)
        dim: int = edges[0].get_dim()

        timestamps: tp.List[float] = [edge.get_timestamp() for edge in edges]
        data: np.ndarray = cls.estimate_variances(edges, window)

        fig: plt.Figure = cls.create_fig(name, dim)
        for i, ax in enumerate(fig.axes):
            ax.plot(timestamps, data[i, :])
        fig.show()
        return fig

    @classmethod
    def plot_group_estimate_variance(
            cls,
            graphs: tp.List['SubGraph'],
            name: str,
            window: int = 50
    ) -> plt.Figure:
        assert cls.is_group_eligible(graphs, name)

        first_edges: tp.List['SubEdge'] = graphs[0].get_of_name(name)

        size: int = len(first_edges)
        dim: int = first_edges[0].get_dim()

        variances: tp.List[np.ndarray] = []
        for graph in graphs:
            edges: tp.List['SubEdge'] = graph.get_of_name(name)
            variances.append(cls.estimate_variances(edges, window))

        mean_set: np.ndarray = np.zeros((dim, size))
        std_set: np.ndarray = np.zeros((dim, size))

        timestamps: tp.List[float] = []
        for i, edge in enumerate(first_edges):
            timestamps.append(edge.get_timestamp())
            for j in range(dim):
                values: tp.List[float] = [variance[j, i] for variance in variances]
                mean_set[j, i] = float(np.mean(values))
                std_set[j, i] = float(np.std(values))
            update_print(f'\r{100 * i / size:.2f}%')
        update_print('\rDone!\n')

        fig: plt.Figure = cls.create_fig(name, dim)
        for i, ax in enumerate(fig.axes):
            means = mean_set[i, :]
            stds = std_set[i, :]
            ax.plot(timestamps, means)
            ax.fill_between(timestamps, means - stds, means + stds, alpha=0.2)
        fig.show()
        return fig

    @classmethod
    def plot_edge_variance(
            cls,
            graph: 'SubGraph',
            name: str
    ) -> plt.Figure:
        assert cls.is_eligible(graph, name)

        edges: tp.List['SubEdge'] = graph.get_of_name(name)
        size: int = len(edges)
        dim: int = edges[0].get_dim()

        timestamps: tp.List[float] = []
        data: np.ndarray = np.zeros((dim, size))
        for i, edge in enumerate(edges):
            timestamps.append(edge.get_timestamp())
            cov_diagonal: 'SubSizeVector' = edge.get_cov_matrix().diagonal()
            for j in range(dim):
                data[j, i] = cov_diagonal[j]

            update_print(f'\r{100 * i / size:.2f}%')
        update_print('\rDone!\n')

        fig: plt.Figure = cls.create_fig(name, dim)
        for i, ax in enumerate(fig.axes):
            ax.plot(timestamps, data[i, :])
        fig.show()
        return fig

    @staticmethod
    def create_fig(name: str, dim: int) -> plt.Figure:
        fig: plt.Figure
        fig, _ = plt.subplots(dim, 1)
        fig.suptitle(f"Edge variance of '{name}'")
        for ax in fig.axes:
            ax.set_xlabel(r'Time [s]')
            ax.set_ylabel(r'Variance [-]')
        return fig


class Analyser(object):
    _fig: tp.Optional[plt.Figure]

    _topology: tp.Type[AnalyserTopology]
    _ate: AnalyserATE
    _rpet: AnalyserRPET
    _rper: AnalyserRPER
    _parameter_values: tp.Type[AnalyserParameterValues]
    _parameter_dynamics: tp.Type[AnalyserParameterDynamics]
    _variance: tp.Type[AnalyserVariance]

    def __init__(self):
        self._fig = None

        self._topology = AnalyserTopology
        self._ate = AnalyserATE()
        self._rpet = AnalyserRPET()
        self._rper = AnalyserRPER()
        self._parameter_values = AnalyserParameterValues
        self._parameter_dynamics = AnalyserParameterDynamics
        self._variance = AnalyserVariance

    def has_fig(self) -> bool:
        return self._fig is not None

    def set_fig(self, fig: plt.Figure) -> None:
        self._fig = fig

    def get_fig(self) -> plt.Figure:
        assert self.has_fig()
        return self._fig

    def save_fig(
            self,
            name: tp.Optional[str] = None
    ) -> None:
        assert self.has_fig()
        fig: plt.Figure = self._fig
        FigureParser.save(fig, name)

    def clear(self) -> None:
        self._ate.clear()
        self._rpet.clear()
        self._rper.clear()

    def topology(self) -> tp.Type[AnalyserTopology]:
        return self._topology

    def ate(self) -> AnalyserATE:
        return self._ate

    def rpet(self) -> AnalyserRPET:
        return self._rpet

    def rper(self) -> AnalyserRPER:
        return self._rper

    def parameter_values(self) -> tp.Type[AnalyserParameterValues]:
        return self._parameter_values

    def parameter_dynamics(self) -> tp.Type[AnalyserParameterDynamics]:
        return self._parameter_dynamics

    def variance(self) -> tp.Type[AnalyserVariance]:
        return self._variance