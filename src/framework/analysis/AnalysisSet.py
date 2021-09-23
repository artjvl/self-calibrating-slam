import pathlib
import pickle as pkl
import sys
import typing as tp
from scipy.stats import norm
import numpy as np
from matplotlib import pyplot as plt
from src.definitions import get_project_root

if tp.TYPE_CHECKING:
    from src.framework.graph.CalibratingGraph import SubCalibratingGraph
    from src.framework.graph.types.nodes.ParameterNode import SubParameterNode
    from src.framework.math.matrix.vector.Vector import SubSizeVector

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
    _first: tp.Optional['SubCalibratingGraph']
    _resolution: int = 30

    _metrics: SubTimeData
    _par_evolution: tp.Dict[str, SubTimeData]
    _par_values: tp.Dict[str, SubTimeData]

    def __init__(self):
        self._first = None
        self._metrics = TimeData()
        self._par_evolution = {}
        self._par_values = {}

    def path(self) -> pathlib.Path:
        return self._path

    def has_first(self) -> bool:
        return self._first is not None

    def first(self) -> 'SubCalibratingGraph':
        assert self.has_first()
        return self._first

    def graph(self) -> 'SubCalibratingGraph':
        return self.first()

    def add_graph(self, graph: 'SubCalibratingGraph') -> None:
        assert graph.has_truth()
        if not self.has_first():
            self._first = graph
        else:
            assert self._first.is_equivalent(graph)

        # metrics
        time: tp.List[float] = []
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
            timestamp: float = subgraph.timestamp()
            time.append(timestamp)
            ate.append(subgraph.get_ate())
            rpet.append(subgraph.get_rpe_translation())
            rper.append(subgraph.get_rpe_rotation())

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

        self._metrics.add(time, 'ate', ate)
        self._metrics.add(time, 'rpet', rpet)
        self._metrics.add(time, 'rper', rper)

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
                    parameter: 'SubParameterNode' = parameters[0]
                    dim: int = parameter.get_dim()
                    vector: 'SubSizeVector' = parameter.to_vector()
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
    def plot_ate(
            self,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        return self.plot_metric('ATE', 'ate', index=index, colour=colour, fig=fig)

    def plot_rept(
            self,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            fig: tp.Optional[plt.Figure] = None) -> plt.Figure:
        return self.plot_metric('RPE (translation)', 'rpet', index=index, colour=colour, fig=fig)

    def plot_repr(
            self,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        return self.plot_metric('RPE (rotation)', 'rper', index=index, colour=colour, fig=fig)

    def plot_metric(
            self,
            text: str,
            key: str,
            index: tp.Optional[int] = None,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        # construct figure
        if fig is None:
            fig = self.create_metric_fig(text)

        # plot data
        ax: plt.Axes = fig.axes[0]
        time: tp.List[float] = self._metrics.time()
        if index is None:
            num_rows: int = self._metrics.num_rows(key)
            for i in range(num_rows):
                ax.plot(time, self._metrics.row(key, i), color=colour)
        else:
            ax.plot(time, self._metrics.row(key, index), color=colour)
        fig.show()
        return fig

    def plot_ate_band(
            self,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        return self.plot_metric_band('ATE', 'ate', colour=colour, fig=fig)

    def plot_rept_band(
            self,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        return self.plot_metric_band('RPE (translation)', 'rpet', colour=colour, fig=fig)

    def plot_repr_band(
            self,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        return self.plot_metric_band('RPE (rotation)', 'rper', colour=colour, fig=fig)

    def plot_metric_band(
            self,
            text: str,
            key: str,
            colour: tp.Optional[str] = None,  # b, g, r, c, m, y, k, w
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        # construct figure
        if fig is None:
            fig = self.create_metric_fig(text)

        # plot data
        ax: plt.Axes = fig.axes[0]
        time: tp.List[float] = self._metrics.time()
        mean: np.ndarray = self._metrics.mean(key)
        std: np.ndarray = self._metrics.std(key)
        ax.plot(time, mean, color=colour)
        if colour is None:
            colour = ax.lines[-1].get_color()
        ax.fill_between(
            time, mean - std, mean + std,
            color=colour, alpha=0.1
        )
        for r in range(1, self._resolution + 1):
            factor: float = norm.pdf(1 + r / (1 * self._resolution), 1, 0.4)
            # factor: float = r / self._resolution
            ax.fill_between(
                time, mean - factor * std, mean + factor * std,
                alpha=0.4 / self._resolution, color=colour, linewidth=0.)
        fig.show()
        return fig

    @staticmethod
    def create_metric_fig(text: str) -> plt.Figure:
        fig, ax = plt.subplots()
        ax.set_title(f'{text} - time')
        ax.set_xlabel(f'Time [s]')
        ax.set_ylabel(f'{text} [m]')
        return fig

    # parameter
    def plot_parameter_evolution(
            self,
            name: str,
            index: tp.Optional[int] = None,
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        assert name in self._par_evolution
        return self.plot_parameter(f"Evolution of parameter '{name}' over time", self._par_evolution[name], index=index, fig=fig)

    def plot_parameter_values(
            self,
            name: str,
            index: tp.Optional[int] = None,
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        assert name in self._par_values
        return self.plot_parameter(f"Values of parameter '{name}' over time", self._par_values[name], index=index, fig=fig)

    def plot_parameter(
            self,
            text: str,
            time_data: SubTimeData,
            index: tp.Optional[int] = None,
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        dim: int = time_data.dim()

        # construct figure
        if fig is None:
            fig = self.create_parameter_fig(dim)
        fig.suptitle(text)

        # plot data
        assert len(fig.axes) == dim

        time: tp.List[float] = time_data.time()
        if index is None:
            for d, ax in enumerate(fig.axes):
                num_rows: int = time_data.num_rows(d)
                for i in range(num_rows):
                    ax.plot(time, time_data.row(d, i))
        else:
            for d, ax in enumerate(fig.axes):
                ax.plot(time, time_data.row(d, index))
        fig.show()
        return fig

    def plot_parameter_evolution_band(
            self,
            name: str,
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        assert name in self._par_evolution
        return self.plot_parameter_band(f"Evolution of parameter '{name}' over time", self._par_evolution[name], fig=fig)

    def plot_parameter_values_band(
            self,
            name: str,
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        assert name in self._par_values
        return self.plot_parameter_band(f"Values of parameter '{name}' over time", self._par_values[name], fig=fig)

    def plot_parameter_band(
            self,
            text: str,
            time_data: SubTimeData,
            fig: tp.Optional[plt.Figure] = None
    ) -> plt.Figure:
        dim: int = time_data.dim()

        # construct figure
        if fig is None:
            fig = self.create_parameter_fig(dim)
        fig.suptitle(text)

        # plot data
        assert len(fig.axes) == dim
        time: tp.List[float] = time_data.time()
        for d, ax in enumerate(fig.axes):
            mean: np.ndarray = time_data.mean(d)
            std: np.ndarray = time_data.std(d)
            ax.plot(time, mean, color=colour)
            if colour is None:
                colour = ax.lines[-1].get_color()
            ax.fill_between(
                time, mean - std, mean + std,
                color=colour, alpha=0.1
            )
            for r in range(1, self._resolution + 1):
                factor: float = norm.pdf(1 + r / (1 * self._resolution), 1, 0.4)
                # factor: float = r / self._resolution
                ax.fill_between(
                    time, mean - factor * std, mean + factor * std,
                    alpha=0.4 / self._resolution, color=colour, linewidth=0.)
        fig.show()
        return fig

    @staticmethod
    def create_parameter_fig(dim: int) -> plt.Figure:
        fig, _ = plt.subplots(dim, 1)
        for d, ax in enumerate(fig.axes):
            ax.set_title(f'Element {d + 1}')
            ax.set_xlabel(f'Time [s]')
            ax.set_ylabel(f'Value [-]')
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
        assert path.is_file()
        with open(path, 'rb') as file:
            instance: 'SubAnalysisSet' = pkl.load(file)
        print(f"src/AnalysisSet: Instance loaded from '{path}'")
        return instance
