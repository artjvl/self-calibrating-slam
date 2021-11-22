import typing as tp

from matplotlib import pyplot as plt
from src.framework.analysis.sim.GraphData import GraphData
from src.framework.analysis.plot.Plotter import Plotter

if tp.TYPE_CHECKING:
    from src.framework.analysis.sim.GraphData import SubGraphData

colours: tp.List[str] = ['#1f77b4', '#ff7f0e']
default_figsize: tp.Tuple[float, float] = (4., 3.)
x_spacing: int = 25


class PlotSim(object):
    _name: str
    _names: tp.List[str]
    _datas: tp.List['SubGraphData']
    _labels: tp.Optional[tp.List[str]]

    def __init__(
            self,
            name: str,
            sims: tp.List[str],
            labels: tp.Optional[tp.List[str]] = None
    ):
        self._name = name

        if labels is not None:
            assert len(sims) == len(labels)
        self._names = sims
        self._datas = []
        for sim in sims:
            self._datas.append(GraphData.load(sim))
        self._labels = labels

    def plot_ate(self) -> plt.Figure:
        fig: tp.Optional[plt.Figure] = None
        for data in self._datas:
            fig = data.plot_ate(fig=fig, show=False, figsize=default_figsize)
        plotter: Plotter = Plotter(fig)
        if self._labels is not None:
            plotter.legend(self._labels)
        plotter.spacing(x_spacing=x_spacing, y_spacing=0.2)
        plotter.save(f'{self._name}_ate')
        plotter.show()
        return fig

    def plot_rpet(self) -> plt.Figure:
        fig: tp.Optional[plt.Figure] = None
        for data in self._datas:
            fig = data.plot_rpet(fig=fig, show=False, figsize=default_figsize)
        plotter: Plotter = Plotter(fig)
        if self._labels is not None:
            plotter.legend(self._labels)
        plotter.spacing(x_spacing=25., y_spacing=None)
        plotter.save(f'{self._name}_rpet')
        plotter.show()
        return fig

    def plot_rper(self) -> plt.Figure:
        fig: tp.Optional[plt.Figure] = None
        for data in self._datas:
            fig = data.plot_rper(fig=fig, show=False, figsize=default_figsize)
        plotter: Plotter = Plotter(fig)
        if self._labels is not None:
            plotter.legend(self._labels)
        plotter.spacing(x_spacing=25., y_spacing=None)
        plotter.save(f'{self._name}_rper')
        plotter.show()
        return fig

    def plot_cost(self) -> plt.Figure:
        fig: tp.Optional[plt.Figure] = None
        for data in self._datas:
            fig = data.plot_cost(fig=fig, show=False, figsize=default_figsize)
        plotter: Plotter = Plotter(fig)
        if self._labels is not None:
            plotter.legend(self._labels)
        plotter.spacing(x_spacing=25., y_spacing=None)
        plotter.save(f'{self._name}_cost')
        plotter.show()
        return fig

    def plot_par(self, name: str) -> plt.Figure:
        fig: tp.Optional[plt.Figure] = None
        # fig1 = None
        for data in self._datas:
            if data.has_parameter(name):
                fig = data.plot_parameter(name, fig=fig, show=False, colour=colours[1], figsize=default_figsize)
                # fig1 = data.plot_parameter_evolution(name, fig=fig1, show=False, colour=colours[1], figsize=default_figsize)
        plotter: Plotter = Plotter(fig)
        plotter.y_limits(-0.04, 0.19)
        plotter.y_label(r'$x_{\mathrm{par}}$ [-]', 0)
        plotter.y_label(r'$y_{\mathrm{par}}$ [-]', 1)
        plotter.y_label(r'$\theta_{\mathrm{par}}$ [-]', 2)
        plotter.spacing(x_spacing=x_spacing, y_spacing=0.05)
        plotter.save(f'{self._name}_par')
        plotter.show()
        # fig1.show()
        return fig

    def plot_meas(self, name: str) -> plt.Figure:
        fig: tp.Optional[plt.Figure] = None
        for data in self._datas:
            if data.has_edge_name(name):
                fig = data.plot_measurements(name, fig=fig, show=False, colour=colours[1], show_individual=True, show_mean=False, figsize=default_figsize)
        plotter: Plotter = Plotter(fig)
        plotter.set_title('Odometry measurements - time (Manhattan)', 0)
        plotter.y_limits(-1.8, 1.8)
        plotter.y_label(r'$x_{\mathrm{meas}}$ [-]', 0)
        plotter.y_label(r'$y_{\mathrm{meas}}$ [-]', 1)
        plotter.y_label(r'$\theta_{\mathrm{meas}}$ [-]', 2)
        plotter.spacing(x_spacing=x_spacing, y_spacing=0.8)
        plotter.save(f'{self._name}_meas')
        plotter.show()
        return fig
