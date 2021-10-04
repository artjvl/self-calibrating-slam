import copy
import pathlib
import pickle as pkl
import sys
import typing as tp

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import norm
from src.definitions import get_project_root
from src.framework.graph.protocols.Visualisable import Visualisable, DrawPoint, DrawAxis, DrawEdge
from src.gui.viewer.Rgb import Rgb

if tp.TYPE_CHECKING:
    from src.framework.graph.CalibratingGraph import SubCalibratingGraph
    from src.framework.graph.Graph import SubGraph, SubNode, SubElement
    from src.framework.graph.types.nodes.ParameterNode import SubParameterNode
    from src.framework.math.lie.transformation import SE2
    from src.framework.math.matrix.vector.Vector import SubSizeVector, Vector2, Vector3

Key = tp.Union[int, str]
SubTimeData = tp.TypeVar('SubTimeData', bound='TimeData')
SubAnalysisSet = tp.TypeVar('SubAnalysisSet', bound='AnalysisSet')


class TimeData(object):
    _time: tp.List[float]
    _data: tp.Dict[Key, np.ndarray]

    def __init__(self):
        self._time = []
        self._data = {}

    def dim(self) -> int:
        assert self.has_first()
        return len(self._data.keys())

    def has_first(self) -> bool:
        return bool(self._time)

    def has_key(self, key: Key) -> bool:
        return key in self._data

    def add(
            self,
            time: tp.List[float],
            key: Key,
            value: tp.List[float]
    ) -> None:
        if not self.has_first():
            self._time = time
        assert len(value) == len(self._time)

        if key not in self._data:
            self._data[key] = np.array([value])
        else:
            self._data[key] = np.vstack((self._data[key], [value]))

    def time(self) -> tp.List[float]:
        assert self.has_first()
        return self._time

    def data(self, key: Key) -> np.ndarray:
        assert self.has_first()
        assert self.has_key(key)
        return self._data[key]

    def num_rows(self, key: Key) -> int:
        data: np.ndarray = self.data(key)
        return data.shape[0]

    def row(self, key: Key, row: int) -> np.ndarray:
        data: np.ndarray = self.data(key)
        return data[row, :]

    def mean(self, key: Key) -> np.ndarray:
        return np.mean(self.data(key), axis=0)

    def std(self, key: Key) -> np.ndarray:
        return np.std(self.data(key), axis=0)


class AnalysisSet(object):
    _path: pathlib.Path = (get_project_root() / 'plots').resolve()
    _graphs: tp.List['SubCalibratingGraph']
    _resolution: int = 30

    _metrics: SubTimeData
    _par_evolution: tp.Dict[str, SubTimeData]
    _par_values: tp.Dict[str, SubTimeData]

    def __init__(self):
        self._graphs = []
        self._metrics = TimeData()
        self._par_evolution = {}
        self._par_values = {}

    def path(self) -> pathlib.Path:
        return self._path

    def has_first(self) -> bool:
        return len(self._graphs) > 0

    def graph(self, index: int) -> 'SubCalibratingGraph':
        assert len(self._graphs) > index
        return self._graphs[index]

    def add_graph(self, graph: 'SubCalibratingGraph') -> None:
        assert graph.has_truth()
        if self.has_first():
            assert self._graphs[0].is_equivalent(graph)
        self._graphs.append(copy.copy(graph))

        # metrics
        time_: tp.List[float] = []
        error: tp.List[float] = []
        ate: tp.List[float] = []
        rpet: tp.List[float] = []
        rper: tp.List[float] = []

        # parameter evolution
        par_time: tp.Dict[str, tp.List[float]] = {}
        par_data: tp.Dict[str, tp.List[tp.List[float]]] = {}

        names: tp.List[str] = graph.get_parameter_names()
        subgraphs: tp.List['SubCalibratingGraph'] = graph.subgraphs()
        size: int = len(subgraphs)
        for i, subgraph in enumerate(subgraphs):
            # metrics
            timestamp: float = subgraph.timestep()
            time_.append(timestamp)
            error.append(subgraph.cost())
            ate.append(subgraph.ate())
            rpet.append(subgraph.rpe_translation())
            rper.append(subgraph.rpe_rotation())

            # parameter evolution
            for name in names:
                if subgraph.has_name(name) and len(graph.get_of_name(name)) == 1:
                    parameter: 'SubParameterNode' = subgraph.get_of_name(name)[0]
                    dim: int = parameter.get_dim()
                    vector: 'SubSizeVector' = parameter.to_vector()
                    if name not in par_data:
                        par_data[name] = [[] for _ in range(dim)]
                        par_time[name] = []

                    par_time[name].append(timestamp)
                    for d in range(dim):
                        par_data[name][d].append(vector[d])
            self.print(f'\rframework/AnalysisSet: Analysing: {100 * i / size:.2f}%')
        self.print('\rframework/AnalysisSet: Analysis done!\n')

        self._metrics.add(time_, 'error', error)
        self._metrics.add(time_, 'ate', ate)
        self._metrics.add(time_, 'rpet', rpet)
        self._metrics.add(time_, 'rper', rper)

        for name, list_ in par_data.items():
            if name not in self._par_evolution:
                self._par_evolution[name] = TimeData()
            dim: int = len(list_)
            for d in range(dim):
                self._par_evolution[name].add(par_time[name], d, par_data[name][d])

        # parameter set
        par_time = {}
        par_data = {}
        for name in names:
            if graph.has_name(name):
                parameters: tp.List['SubParameterNode'] = graph.get_of_name(name)
                if len(parameters) > 1:
                    first: 'SubParameterNode' = parameters[0]
                    dim: int = first.get_dim()
                    vector: 'SubSizeVector' = first.to_vector()
                    if name not in par_data:
                        par_data[name] = [[] for _ in range(dim)]
                        par_time[name] = []
                    for parameter in parameters:
                        par_time[name].append(parameter.get_timestamp())
                        for d in range(dim):
                            par_data[name][d].append(vector[d])
        for name, list_ in par_data.items():
            if name not in self._par_values:
                self._par_values[name] = TimeData()
            dim: int = len(list_)
            for d in range(dim):
                self._par_values[name].add(par_time[name], d, par_data[name][d])

    @staticmethod
    def print(text: str) -> None:
        sys.__stdout__.write(f'\r{text}')
        sys.__stdout__.flush()

    # metrics
    def plot_error(
            self,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        return self.plot_metric(
            'Cost', '-', 'error',
            index=index, colour=colour, alpha=alpha, linestyle=linestyle,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_ate(
            self,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        return self.plot_metric(
            'ATE', 'm', 'ate',
            index=index, colour=colour, alpha=alpha, linestyle=linestyle,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_rpet(
            self,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        return self.plot_metric(
            'RPE (translation)', 'm', 'rpet',
            index=index, colour=colour, alpha=alpha, linestyle=linestyle,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_rper(
            self,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        return self.plot_metric(
            'RPE (rotation)', 'rad', 'rper',
            index=index, colour=colour, alpha=alpha, linestyle=linestyle,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_metric(
            self,
            metric_name: str,
            unit: str,
            key: str,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        # construct figure
        if fig is None:
            fig = self.create_metric_fig(metric_name, unit, figsize=figsize)

        # plot data
        ax: plt.Axes = fig.axes[0]
        time: tp.List[float] = self._metrics.time()
        if index is None:
            num_rows: int = self._metrics.num_rows(key)
            for i in range(num_rows):
                ax.plot(time, self._metrics.row(key, i), color=colour, alpha=alpha, linestyle=linestyle, linewidth=1)
        else:
            ax.plot(time, self._metrics.row(key, index), color=colour, alpha=alpha, linestyle=linestyle)
        if should_show:
            fig.show()
        return fig

    def plot_error_band(
            self,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            show_band: bool = True,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        return self.plot_metric_band(
            'Cost', '-', 'error',
            colour=colour, alpha=alpha, linestyle=linestyle, show_band=show_band,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_ate_band(
            self,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            show_band: bool = True,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        return self.plot_metric_band(
            'ATE', 'm', 'ate',
            colour=colour, alpha=alpha, linestyle=linestyle, show_band=show_band,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_rpet_band(
            self,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            show_band: bool = True,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        return self.plot_metric_band(
            'RPE (translation)', 'm', 'rpet',
            colour=colour, alpha=alpha, linestyle=linestyle, show_band=show_band,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_rper_band(
            self,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            show_band: bool = True,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        return self.plot_metric_band(
            'RPE (rotation)', 'rad', 'rper',
            colour=colour, alpha=alpha, linestyle=linestyle, show_band=show_band,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_metric_band(
            self,
            metric_name: str,
            unit: str,
            key: str,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            show_band: bool = True,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        # construct figure
        if fig is None:
            fig = self.create_metric_fig(metric_name, unit, figsize=figsize)

        # plot data
        ax: plt.Axes = fig.axes[0]
        time: tp.List[float] = self._metrics.time()
        mean: np.ndarray = self._metrics.mean(key)
        std: np.ndarray = self._metrics.std(key)
        ax.plot(time, mean, alpha=alpha, color=colour, linestyle=linestyle)
        if colour is None:
            colour = ax.lines[-1].get_color()
        if show_band:
            ax.fill_between(
                time, mean - std, mean + std,
                color=colour, alpha=0.1 * alpha
            )
            for r in range(1, self._resolution + 1):
                factor: float = norm.pdf(1 + r / (1 * self._resolution), 1, 0.4)
                # factor: float = r / self._resolution
                ax.fill_between(
                    time, mean - factor * std, mean + factor * std,
                    alpha=alpha * 0.4 / self._resolution, color=colour, linewidth=0.)
        if should_show:
            fig.show()
        return fig

    @staticmethod
    def create_metric_fig(
            metric_name: str,
            unit: str,
            figsize: tp.Tuple[float, float] = (5, 4)
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title(f'{metric_name} - time')
        ax.set_xlabel(f'Time [s]')
        ax.set_ylabel(f'{metric_name} [{unit}]')
        return fig

    # parameter
    def plot_parameter_evolution(
            self,
            parameter_name: str,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        assert parameter_name in self._par_evolution
        return self.plot_parameter(
            parameter_name, self._par_evolution[parameter_name],
            index=index, colour=colour, alpha=alpha, linestyle=linestyle,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_parameter_values(
            self,
            parameter_name: str,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        assert parameter_name in self._par_values
        return self.plot_parameter(
            parameter_name, self._par_values[parameter_name],
            index=index, colour=colour, alpha=alpha, linestyle=linestyle,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_parameter(
            self,
            parameter_name: str,
            time_data: SubTimeData,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        dim: int = time_data.dim()

        # construct figure
        if fig is None:
            fig = self.create_parameter_fig(dim, parameter_name, figsize=figsize)

        # plot data
        assert len(fig.axes) == dim

        time: tp.List[float] = time_data.time()
        if index is None:
            for d, ax in enumerate(fig.axes):
                num_rows: int = time_data.num_rows(d)
                for i in range(num_rows):
                    ax.plot(time, time_data.row(d, i), color=colour, alpha=alpha, linestyle=linestyle, linewidth=1)
        else:
            for d, ax in enumerate(fig.axes):
                ax.plot(time, time_data.row(d, index), color=colour, alpha=alpha, linestyle=linestyle)
        if should_show:
            fig.show()
        return fig

    def plot_parameter_evolution_band(
            self,
            parameter_name: str,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            show_band: bool = True,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        assert parameter_name in self._par_evolution
        return self.plot_parameter_band(
            parameter_name, self._par_evolution[parameter_name],
            colour=colour, alpha=alpha, linestyle=linestyle, show_band=show_band,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_parameter_values_band(
            self,
            parameter_name: str,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            show_band: bool = True,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        assert parameter_name in self._par_values
        return self.plot_parameter_band(
            parameter_name, self._par_values[parameter_name],
            colour=colour, alpha=alpha, linestyle=linestyle, show_band=show_band,
            fig=fig, figsize=figsize, should_show=should_show
        )

    def plot_parameter_band(
            self,
            parameter_name: str,
            time_data: SubTimeData,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-',
            show_band: bool = True,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = (5, 4),
            should_show: bool = True
    ) -> plt.Figure:
        dim: int = time_data.dim()

        # construct figure
        if fig is None:
            fig = self.create_parameter_fig(dim, parameter_name, figsize=figsize)

        # plot data
        assert len(fig.axes) == dim
        time: tp.List[float] = time_data.time()
        for d, ax in enumerate(fig.axes):
            mean: np.ndarray = time_data.mean(d)
            std: np.ndarray = time_data.std(d)
            ax.plot(time, mean, color=colour, linestyle=linestyle)
            if colour is None:
                colour = ax.lines[-1].get_color()
            if show_band:
                ax.fill_between(
                    time, mean - std, mean + std,
                    color=colour, alpha=0.1 * alpha
                )
                for r in range(1, self._resolution + 1):
                    factor: float = norm.pdf(1 + r / (1 * self._resolution), 1, 0.4)
                    # factor: float = r / self._resolution
                    ax.fill_between(
                        time, mean - factor * std, mean + factor * std,
                        color=colour, alpha=alpha * 0.4 / self._resolution, linewidth=0.)
        if should_show:
            fig.show()
        return fig

    @staticmethod
    def create_parameter_fig(
            dim: int,
            parameter_name: str,
            figsize: tp.Tuple[float, float] = (5, 4)
    ) -> plt.Figure:
        fig, _ = plt.subplots(dim, 1, figsize=figsize)
        for d, ax in enumerate(fig.axes):
            ax.set_title(f"Parameter '{parameter_name}' [{d + 1}/{dim}] - time")
            ax.set_ylabel(f'Value [-]')
            if d != dim - 1:
                ax.xaxis.set_ticklabels([])

        fig.axes[-1].set_xlabel(f'Time [s]')
        return fig

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
                        point: 'SubSizeVector' = element.draw_point()
                        x_min = min(x_min, point[0])
                        x_max = max(x_max, point[0])
                        y_min = min(y_min, point[1])
                        y_max = max(y_max, point[1])
        return x_min, y_min, x_max - x_min, y_max - y_min

    def plot_topology(self) -> plt.Figure:
        import time
        graph: 'SubGraph' = self._first

        _, __, size_x, size_y = self.find_domain(graph)
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

    # save load
    def save(self, path: tp.Union[str, pathlib.Path]) -> None:
        if isinstance(path, str):
            if not path.endswith('.pickle'):
                path += '.pickle'
            self._path.mkdir(parents=True, exist_ok=True)
            path: pathlib.Path = (self._path / path).resolve()
        with open(path, 'wb') as file:
            pkl.dump(self, file)
        print(f"src/AnalysisSet: Instance saved as '{path}'")

    @classmethod
    def load(cls, path: tp.Union[str, pathlib.Path]) -> 'SubAnalysisSet':
        if isinstance(path, str):
            if not path.endswith('.pickle'):
                path += '.pickle'
            path: pathlib.Path = (cls._path / path).resolve()
        assert path.is_file(), path
        with open(path, 'rb') as file:
            instance: 'SubAnalysisSet' = pkl.load(file)
        print(f"src/AnalysisSet: Instance loaded from '{path}'")
        return instance
