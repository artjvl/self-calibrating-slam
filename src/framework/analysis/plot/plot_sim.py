from src.framework.analysis.plot.Plotter import Plotter
from src.framework.analysis.plot.PlotSim import PlotSim

path: str = 'manhattan'
fluc: str = 'sin'
sim: str = 'timely'
spec: str = 'bias'
size: int = 20

name = f'{path}_{fluc}-{spec}-0.1_without-vs-{sim}'
names = [
    f'{path}_{fluc}-{spec}_without-1-{size}',
    f'{path}_{fluc}-{spec}_{sim}-10-{size}'
]

plot_sim = PlotSim(
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