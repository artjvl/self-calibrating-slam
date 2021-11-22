import typing as tp

import numpy as np
from matplotlib import pyplot as plt

from src.framework.analysis.plot.PlotSim import PlotSim
from src.framework.analysis.plot.Plotter import Plotter

if tp.TYPE_CHECKING:
    from src.framework.analysis.sim.GraphData import SubGraphData

path: str = 'manhattan'
fluc: str = 'sin'
sim: str = 'timely'
spec: str = 'bias'

name = f'{path}_{fluc}-{spec}_without-vs-{sim}'
names = [
    f'{path}_{fluc}-{spec}_without-1-20',
    f'{path}_{fluc}-{spec}_{sim}-10-20'
]

SubSinFunction = tp.TypeVar('SubSinFunction', bound='SinFunction')


class SinFunction(object):
    _factor: int
    def __init__(
            self,
            factor: int = 1
    ):
        self._factor = factor

    def set_factor(self, factor: int) -> SubSinFunction:
        self._factor = factor
        return self

    def function(self, x) -> tp.Callable:
        return 0.1 * np.sin(self._factor * 2 * np.pi * x / 200.)

def f_sin(
        x: float,
        factor: int = 1
) -> float:
    return 0.1 * np.sin(factor * 2 * np.pi * x / 200.)


class PlotSimSin(PlotSim):
    def plot_par(self, name: str) -> plt.Figure:
        fig: plt.Figure = super().plot_par(name)
        first: 'SubGraphData' = self._datas[0]
        function = SinFunction()
        for d, ax in enumerate(fig.axes):
            f = function.set_factor(d + 1).function
            t = np.array(first.time())
            ax.plot(t, f(t), color='k', linestyle='--', linewidth=1.)
        plotter: Plotter = Plotter(fig)
        plotter.save(f'{self._name}_par')
        plotter.show()
        return fig

plot_sim = PlotSimSin(
    name,
    names,
    ['no par. (mean)', f'{sim} par. (mean)']
)

plot_sim.plot_ate()
plot_sim.plot_rpet()
plot_sim.plot_rper()
plot_sim.plot_cost()
plot_sim.plot_par(spec)
plot_sim.plot_meas('wheel')