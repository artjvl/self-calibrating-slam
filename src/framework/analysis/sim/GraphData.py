import copy
import pathlib
import pickle as pkl
import sys
import typing as tp

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker
from scipy.stats import norm
from src.definitions import get_project_root
from src.framework.analysis.sim.TimeData import Data, TimeData
from src.framework.graph.Visualisable import Visualisable, DrawPoint, DrawAxis, DrawEdge
from src.gui.viewer.Rgb import Rgb

if tp.TYPE_CHECKING:
    from src.framework.analysis.sim.TimeData import SubData, SubTimeData
    from src.framework.graph.Graph import SubNode, SubParameterNode, SubEdge, SubNodeEdge, SubGraph
    from src.framework.math.lie.transformation import SE2
    from src.framework.math.matrix.vector.Vector import SubSizeVector, Vector2, Vector3

default_figsize: tp.Tuple[float, float] = (4, 2.4)  # (4, 3.2)

SubGraphData = tp.TypeVar('SubGraphData', bound='GraphData')


class GraphData(object):
    _ATE: str = 'ate'
    _COST: str = 'cost'
    _RPET: str = 'rpet'
    _RPER: str = 'rper'

    _path: pathlib.Path = (get_project_root() / 'plots').resolve()
    _graphs: tp.List['SubGraph']
    _resolution: int = 30

    _metrics: tp.Optional['SubTimeData']
    _measurements: tp.Dict[str, 'SubTimeData']
    _par_evolution: tp.Dict[str, 'SubTimeData']
    _par_values: tp.Dict[str, 'SubTimeData']
    _par_spatial: tp.Dict[str, 'SubData']

    def __init__(self):
        self._graphs = []
        self._metrics = None
        self._measurements = {}
        self._par_evolution = {}
        self._par_values = {}

    def path(self) -> pathlib.Path:
        return self._path

    def has_first(self) -> bool:
        return len(self._graphs) > 0

    def graph(self, index: int = 0) -> 'SubGraph':
        assert len(self._graphs) > index
        return self._graphs[index]

    def add_graph(self, graph: 'SubGraph') -> None:
        assert graph.has_truth()
        has_first: bool = self.has_first()
        if has_first:
            assert self._graphs[0].is_equivalent(graph)
        self._graphs.append(copy.copy(graph))

        # metrics
        time_: tp.List[float] = []
        error: tp.List[float] = []
        ate: tp.List[float] = []
        rpet: tp.List[float] = []
        rper: tp.List[float] = []

        # parameter evolution
        par_evolution: tp.Dict[str, tp.List[tp.List[float]]] = {}

        # measurements
        meas: tp.Dict[str, tp.List[tp.List[float]]] = {}

        parameter_names: tp.List[str] = graph.get_parameter_names()
        edge_names: tp.List[str] = graph.get_edge_names()
        subgraphs: tp.List['SubGraph'] = graph.subgraphs()
        size: int = len(subgraphs)

        for i, subgraph in enumerate(subgraphs):
            # metrics
            timestep: float = subgraph.timestep()
            time_.append(timestep)
            error.append(subgraph.cost())
            ate.append(subgraph.ate())
            rpet.append(subgraph.rpe_translation())
            rper.append(subgraph.rpe_rotation())

            # parameter evolution
            for parameter_name in parameter_names:
                if subgraph.has_name(parameter_name):
                    parameter: 'SubParameterNode' = subgraph.get_of_name(parameter_name)[0]
                    dim: int = parameter.dim()
                    vector: 'SubSizeVector' = parameter.to_vector()
                    if parameter_name not in par_evolution:
                        par_evolution[parameter_name] = [[] for _ in range(dim + 1)]

                    par_evolution[parameter_name][0].append(timestep)
                    for d in range(dim):
                        par_evolution[parameter_name][d + 1].append(vector[d])

            # measurements
            for edge_name in edge_names:
                if subgraph.has_name(edge_name):
                    edge: 'SubEdge' = subgraph.get_of_name(edge_name)[-1]
                    if edge.timestep() == timestep:
                        dim: int = edge.dim()
                        measurement: 'SubSizeVector' = edge.to_vector()
                        if edge_name not in meas:
                            meas[edge_name] = [[] for _ in range(dim + 1)]

                        meas[edge_name][0].append(timestep)
                        for d in range(dim):
                            meas[edge_name][d + 1].append(measurement[d])

            self.print(f'\rframework/AnalysisSet: Analysing: {100 * i / size:.2f}%')
        self.print('\rframework/AnalysisSet: Analysis done!\n')

        if not has_first:
            self._metrics = TimeData(time_)
        self._metrics.add(self._COST, error)
        self._metrics.add(self._ATE, ate)
        self._metrics.add(self._RPET, rpet)
        self._metrics.add(self._RPER, rper)

        for parameter_name, list_ in par_evolution.items():
            if parameter_name not in self._par_evolution:
                self._par_evolution[parameter_name] = TimeData(par_evolution[parameter_name][0])
            dim: int = len(list_) - 1
            for d in range(dim):
                self._par_evolution[parameter_name].add(d, par_evolution[parameter_name][d + 1])

        for edge_name, list_ in meas.items():
            if edge_name not in self._measurements:
                self._measurements[edge_name] = TimeData(meas[edge_name][0])
            dim: int = len(list_) - 1
            for d in range(dim):
                self._measurements[edge_name].add(d, meas[edge_name][d + 1])

        # parameter set
        par_values: tp.Dict[str, tp.List[tp.List[float]]] = {}
        # par_spatial: tp.Dict[str, tp.List[tp.List[float]]] = {}
        for parameter_name in parameter_names:
            if graph.has_name(parameter_name):
                parameters: tp.List['SubParameterNode'] = graph.get_of_name(parameter_name)
                if len(parameters) > 1:
                    dim: int = parameters[0].dim()

                    # parameter values
                    if parameter_name not in par_values:
                        par_values[parameter_name] = [[] for _ in range(dim + 1)]
                    for parameter in parameters:
                        vector: 'SubSizeVector' = parameter.to_vector()
                        par_values[parameter_name][0].append(parameter.get_timestep())
                        for d in range(dim):
                            par_values[parameter_name][d + 1].append(vector[d])

                        # # parameter spatial
                        # if parameter.has_translation():
                        #     if parameter_name not in par_spatial:
                        #         par_spatial[parameter_name] = [[] for _ in range(dim)]
                        #     for d in range(dim):
                        #         par_spatial[parameter_name][d].append(vector[d])

        for parameter_name, list_ in par_values.items():
            if parameter_name not in self._par_values:
                self._par_values[parameter_name] = TimeData(par_values[parameter_name][0])
            dim: int = len(list_) - 1
            for d in range(dim):
                self._par_values[parameter_name].add(d, par_values[parameter_name][d + 1])

        # for parameter_name, list_ in par_spatial.items():
        #     if parameter_name not in self._par_spatial:
        #         self._par_spatial[parameter_name] = Data()
        #     dim: int = len(list_)
        #     for d in range(dim):
        #         self._par_spatial[parameter_name].add(d, par_values[parameter_name][d])

    @staticmethod
    def print(text: str) -> None:
        sys.__stdout__.write(f'\r{text}')
        sys.__stdout__.flush()

    # metrics
    def time(self) -> tp.List[float]:
        return self._metrics.time()

    def plot_cost(
            self,
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:
        return self._plot_metric(
            'Cost', '-', self._COST,
            show_individual=show_individual, show_mean=show_mean, show_band=show_band, show=show, indices=indices,
            fig=fig, figsize=figsize, colour=colour, alpha=alpha, linestyle=linestyle
        )

    def plot_ate(
            self,
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:
        fig: plt.Figure = self._plot_metric(
            'ATE', 'm', self._ATE,
            show_individual=show_individual, show_mean=show_mean, show_band=show_band, show=show, indices=indices,
            fig=fig, figsize=figsize, colour=colour, alpha=alpha, linestyle=linestyle
        )
        print(np.mean(self._metrics.mean(self._ATE)))
        fig.axes[0].yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        return fig

    def plot_rpet(
            self,
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:
        return self._plot_metric(
            'RPE (translation)', 'm', self._RPET,
            show_individual=show_individual, show_mean=show_mean, show_band=show_band, show=show, indices=indices,
            fig=fig, figsize=figsize, colour=colour, alpha=alpha, linestyle=linestyle
        )

    def plot_rper(
            self,
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:
        return self._plot_metric(
            'RPE (rotation)', 'rad', self._RPER,
            show_individual=show_individual, show_mean=show_mean, show_band=show_band, show=show, indices=indices,
            fig=fig, figsize=figsize, colour=colour, alpha=alpha, linestyle=linestyle
        )

    def _plot_metric(
            self,
            metric_name: str,
            unit: str,
            key: str,
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:

        # construct figure
        if fig is None:
            fig = self.create_metric_fig(metric_name, unit, figsize=figsize)

        ax: plt.Axes = fig.axes[0]
        time: tp.List[float] = self._metrics.time()

        # plot individual
        if show_individual:
            if indices is None:
                num_rows: int = self._metrics.num_rows(key)
                indices = list(range(num_rows))
            for i in indices:
                ax.plot(time, self._metrics.row(key, i), color=colour, alpha=alpha, linestyle=linestyle, linewidth=1)

        # plot mean/band
        mean: np.ndarray = self._metrics.mean(key)
        if show_mean:
            ax.plot(time, mean, alpha=alpha, color=colour, linestyle=linestyle)
            if show_band:
                std: np.ndarray = self._metrics.std(key)
                if colour is None:
                    colour = ax.lines[-1].get_color()
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

        if show:
            fig.show()
        return fig

    # parameter
    def get_parameter_evolution_data(
            self,
            parameter_name: str
    ) -> 'SubTimeData':
        assert self.has_parameter_evolution(parameter_name)
        return self._par_evolution[parameter_name]

    def get_parameter_values_data(
            self,
            parameter_name: str
    ) -> 'SubTimeData':
        assert self.has_parameter_values(parameter_name)
        return self._par_values[parameter_name]

    def get_parameter_data(
            self,
            parameter_name: str
    ) -> 'SubTimeData':
        assert self.has_parameter(parameter_name)
        if parameter_name in self._par_values:
            return self._par_values[parameter_name]
        return self._par_evolution[parameter_name]

    def get_parameters(self) -> tp.List[str]:
        return self.get_parameter_evolutions() + self.get_parameter_values()

    def has_parameter(self, parameter_name: str) -> bool:
        return self.has_parameter_evolution(parameter_name) or self.has_parameter_values(parameter_name)

    def plot_parameter(
            self,
            parameter_name: str,
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:
        time_data: 'SubTimeData' = self.get_parameter_data(parameter_name)
        return self._plot_parameter(
            parameter_name, time_data,
            show_individual=show_individual, show_mean=show_mean, show_band=show_band, show=show, indices=indices,
            fig=fig, figsize=figsize, colour=colour, alpha=alpha, linestyle=linestyle
        )

    def has_parameter_evolution(self, parameter_name: str) -> bool:
        return parameter_name in self._par_evolution

    def get_parameter_evolutions(self) -> tp.List[str]:
        return list(self._par_evolution.keys())

    def plot_parameter_evolution(
            self,
            parameter_name: str,
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:
        time_data: 'SubTimeData' = self.get_parameter_evolution_data(parameter_name)
        return self._plot_parameter(
            parameter_name, time_data,
            show_individual=show_individual, show_mean=show_mean, show_band=show_band, show=show, indices=indices,
            fig=fig, figsize=figsize, colour=colour, alpha=alpha, linestyle=linestyle
        )

    def has_parameter_values(self, parameter_name: str) -> bool:
        return parameter_name in self._par_values

    def get_parameter_values(self) -> tp.List[str]:
        return list(self._par_values.keys())

    def plot_parameter_values(
            self,
            parameter_name: str,
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:
        time_data: 'SubTimeData' = self.get_parameter_values_data(parameter_name)
        return self._plot_parameter(
            parameter_name, time_data,
            show_individual=show_individual, show_mean=show_mean, show_band=show_band, show=show, indices=indices,
            fig=fig, figsize=figsize, colour=colour, alpha=alpha, linestyle=linestyle
        )

    def _plot_parameter(
            self,
            parameter_name: str,
            time_data: 'SubTimeData',
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:
        dim: int = time_data.dim()

        # construct figure
        if fig is None:
            fig = self.create_parameter_fig(dim, parameter_name, figsize=figsize)

        assert len(fig.axes) == dim

        # plot data
        time: tp.List[float] = time_data.time()
        for d, ax in enumerate(fig.axes):
            if show_individual:
                if indices is None:
                    num_rows: int = time_data.num_rows(d)
                    indices = list(range(num_rows))
                for i in indices:
                    ax.plot(time, time_data.row(d, i), color=colour, alpha=alpha, linestyle=linestyle, linewidth=1)

            mean: np.ndarray = time_data.mean(d)
            if show_mean:
                ax.plot(time, mean, color=colour, linestyle=linestyle)
                if show_band:
                    std: np.ndarray = time_data.std(d)
                    if colour is None:
                        colour = ax.lines[-1].get_color()
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
        if show:
            fig.show()
        return fig

    # measurements
    def get_edge_names(self) -> tp.List[str]:
        return list(self._measurements.keys())

    def has_edge_name(self, edge_name: str) -> bool:
        return edge_name in self._measurements

    def plot_measurements(
            self,
            edge_name: str,
            show_individual: bool = False,
            show_mean: bool = True,
            show_band: bool = True,
            show: bool = True,
            indices: tp.Optional[tp.List[int]] = None,
            fig: tp.Optional[plt.Figure] = None,
            figsize: tp.Tuple[float, float] = default_figsize,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            alpha: float = 1,
            linestyle: str = '-'
    ) -> plt.Figure:
        self.has_edge_name(edge_name)
        time_data: 'SubTimeData' = self._measurements[edge_name]
        dim: int = time_data.dim()

        # construct figure
        if fig is None:
            fig = self.create_measurement_fig(dim, edge_name, figsize=figsize)

        assert len(fig.axes) == dim

        # plot data
        time: tp.List[float] = time_data.time()
        for d, ax in enumerate(fig.axes):
            if show_individual:
                if indices is None:
                    num_rows: int = time_data.num_rows(d)
                    indices = list(range(num_rows))
                for i in indices:
                    ax.scatter(time, time_data.row(d, i), color=colour, alpha=alpha, linestyle=linestyle, linewidth=1, s=0.5)

            mean: np.ndarray = time_data.mean(d)
            if show_mean:
                ax.plot(time, mean, color=colour, linestyle=linestyle)
                if show_band:
                    std: np.ndarray = time_data.std(d)
                    if colour is None:
                        colour = ax.lines[-1].get_color()
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
        if show:
            fig.show()
        return fig

    # tracking
    def tracking_lsq(
            self,
            parameter_name: str,
            function: tp.Callable,
            index: int = 0
    ) -> tp.List[float]:
        time_data: TimeData = self.get_parameter_data(parameter_name)
        return self._tracking_lsq(time_data, function, index)

    def evolution_tracking_lsq(
            self,
            parameter_name: str,
            function: tp.Callable,
            index: int = 0
    ) -> tp.List[float]:
        time_data: TimeData = self.get_parameter_evolution_data(parameter_name)
        return self._tracking_lsq(time_data, function, index)

    def values_tracking_lsq(
            self,
            parameter_name: str,
            function: tp.Callable,
            index: int = 0
    ) -> tp.List[float]:
        time_data: TimeData = self.get_parameter_values_data(parameter_name)
        return self._tracking_lsq(time_data, function, index)

    @staticmethod
    def _tracking_lsq(
            time_data: 'SubTimeData',
            function: tp.Callable,
            index: int
    ) -> tp.List[float]:
        assert index < time_data.dim()
        time: tp.List[float] = time_data.time()
        mean: np.ndarray = time_data.mean(index)
        return [(mean[i] - function(t)) ** 2 for i, t in enumerate(time)]

    # figs
    @staticmethod
    def create_metric_fig(
            metric_name: str,
            unit: str,
            figsize: tp.Tuple[float, float] = default_figsize
    ) -> plt.Figure:
        fig, ax = plt.subplots(figsize=figsize)
        fig.tight_layout()
        ax.set_title(f'{metric_name} - time')
        ax.set_xlabel(f'Steps [-]')
        ax.set_ylabel(f'{metric_name} [{unit}]')
        return fig

    @staticmethod
    def create_multi_fig(
            dim: int,
            title: str,
            x_label: str,
            y_label: str,
            figsize: tp.Tuple[float, float] = default_figsize
    ) -> plt.Figure:
        fig: plt.Figure = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(dim, hspace=0.2)
        gs.subplots(sharex=True)

        fig.axes[0].set_title(title)
        for d, ax in enumerate(fig.axes):
            ax.set_ylabel(y_label)
            ax.label_outer()

        fig.axes[-1].set_xlabel(x_label)
        return fig

    @classmethod
    def create_parameter_fig(
            cls,
            dim: int,
            parameter_name: str,
            figsize: tp.Tuple[float, float] = default_figsize
    ) -> plt.Figure:
        return cls.create_multi_fig(
            dim,
            f"Parameter '{parameter_name}' - time",
            x_label='Steps [-]',
            y_label='Value [-]',
            figsize=figsize
        )

    @classmethod
    def create_measurement_fig(
            cls,
            dim: int,
            sensor_name: str,
            figsize: tp.Tuple[float, float] = default_figsize
    ) -> plt.Figure:
        return cls.create_multi_fig(
            dim,
            f"Measurements '{sensor_name}' - time",
            x_label='Steps [-]',
            y_label='Value [-]',
            figsize=figsize
        )

    @staticmethod
    def find_domain(graph: 'SubGraph') -> tp.Tuple[float, float, float, float]:
        x_min: float = 0.
        x_max: float = 0.
        y_min: float = 0.
        y_max: float = 0

        type_: tp.Type['SubNode']
        for type_ in graph.get_types():
            if issubclass(type_, Visualisable):
                elements: tp.List['SubNodeEdge'] = graph.get_of_type(type_)
                element: 'SubNodeEdge'
                for element in elements:
                    if isinstance(element, DrawPoint):
                        point: 'SubSizeVector' = element.draw_point()
                        x_min = min(x_min, point[0])
                        x_max = max(x_max, point[0])
                        y_min = min(y_min, point[1])
                        y_max = max(y_max, point[1])
        return x_min, y_min, x_max - x_min, y_max - y_min

    def plot_topology(self, index: int = 0) -> plt.Figure:
        import time
        graph: 'SubGraph' = self._graphs[index]

        _, __, size_x, size_y = self.find_domain(graph)
        fig, ax = plt.subplots(figsize=(6, 6))
        # fig, ax = plt.subplots(figsize=(0.2 * size_x, 0.2 * size_y))

        for type_ in graph.get_types():
            if issubclass(type_, Visualisable):
                t = time.time()
                elements: tp.List['SubNodeEdge'] = graph.get_of_type(type_)
                element: 'SubNodeEdge'
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
    def load(
            cls,
            path: tp.Union[str, pathlib.Path],
            should_print: bool = False
    ) -> 'SubGraphData':
        if isinstance(path, str):
            if not path.endswith('.pickle'):
                path += '.pickle'
            path: pathlib.Path = (cls._path / path).resolve()
        assert path.is_file(), path
        with open(path, 'rb') as file:
            instance: 'SubGraphData' = pkl.load(file)
        if should_print:
            print(f"src/AnalysisSet: Instance loaded from '{path}'")
        return instance
