import typing as tp

import matplotlib
from matplotlib import pyplot as plt
from src.framework.analysis.AnalysisSet import AnalysisSet
from src.framework.analysis.Plotter import Plotter

matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'

# INPUT
config: int = 2
title: str = r'Manhattan path with parameter: $\mathrm{scale}(y) = (1.1)$'
path_id: str = 'manhattan'
par_id: str = 'scale'
sim_id: str = 'constant'
parameter_id: str = 'static'
num_mc_without: int = 10
num_mc_parameter: int = 10

is_ate: bool = True
is_error: bool = True
is_parev: bool = True
is_rper: bool = True
is_rpet: bool = True
is_default: bool = False

parameter = AnalysisSet.load(f'{path_id}_{sim_id}-{par_id}_{parameter_id}-{config}-{num_mc_parameter}')
without = AnalysisSet.load(f'{path_id}_{sim_id}-{par_id}_without-{config}-{num_mc_without}')
sim_name: str = f'{path_id}_{sim_id}-{par_id}-{config}'
colours: tp.List[str] = ['#1f77b4', '#ff7f0e']
fig_name: str = f'without-vs-{parameter_id}'

labels: tp.List[str] = [
    f'no par. (mean)',
    f'{parameter_id} par. (mean)',
    f'{parameter_id} par. (individual)'
]

blue: tp.Dict[str, plt.Line2D] = {
    '-': plt.Line2D([0], [0], color=colours[0], linestyle='-'),
    '--': plt.Line2D([0], [0], color=colours[0], linestyle='--')
}

orange = {
    '-': plt.Line2D([0], [0], color=colours[1], linestyle='-'),
    '--': plt.Line2D([0], [0], color=colours[1], linestyle='--')
}

fig: tp.Optional[plt.Figure]

if is_ate:
    fig = None
    if is_default:  # DEFAULT
        fig = parameter.plot_ate_band(colour=colours[1], fig=fig, should_show=False)
        fig = without.plot_ate_band(colour=colours[0], fig=fig, should_show=False)
    else:  # NON-DEFAULT
        fig = parameter.plot_ate(colour=colours[1], alpha=0.2, fig=fig, should_show=False, linestyle='--')
        fig = parameter.plot_ate_band(colour=colours[1], alpha=1, fig=fig, should_show=False, linestyle='-', show_band=False)
        fig = without.plot_ate_band(colour=colours[0], fig=fig, should_show=False)

    plotter = Plotter(fig)
    if is_default:  # DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    else:  # NON-DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    plotter.set_title(title)
    plotter.save(f'{sim_name}_ate_{fig_name}')
    plotter.show()

if is_error:
    fig = None
    if is_default:  # DEFAULT
        fig = parameter.plot_error_band(colour=colours[1], fig=fig, should_show=False)
        fig = without.plot_error_band(colour=colours[0], fig=fig, should_show=False)
    else:  # NON-DEFAULT
        fig = parameter.plot_error(colour=colours[1], alpha=0.2, fig=fig, should_show=False, linestyle='--')
        fig = parameter.plot_error_band(colour=colours[1], alpha=1, fig=fig, should_show=False, linestyle='-', show_band=False)
        fig = without.plot_error_band(colour=colours[0], fig=fig, should_show=False)

    plotter = Plotter(fig)
    if is_default:  # DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    else:  # NON-DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    plotter.set_title(title)
    plotter.save(f'{sim_name}_error_{fig_name}')
    plotter.show()

if is_parev:
    fig = None
    if is_default:  # DEFAULT
        fig = parameter.plot_parameter_evolution_band(par_id, colour=colours[1], fig=fig, should_show=False)
    else:  # NON-DEFAULT
        fig = parameter.plot_parameter_evolution(par_id, colour=colours[1], alpha=.6, fig=fig, should_show=False, linestyle='--')
        fig = parameter.plot_parameter_evolution_band(par_id, colour=colours[1], alpha=1., fig=fig, should_show=False, linestyle='-', show_band=False)

    plotter = Plotter(fig)
    if is_default:  # DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    else:  # NON-DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    plotter.set_title(title)
    plotter.save(f'{sim_name}_parev_{fig_name}')
    plotter.show()

if is_rper:
    fig = None
    if is_default:  # DEFAULT
        fig = parameter.plot_rper_band(colour=colours[1], fig=fig, should_show=False)
        fig = without.plot_rper_band(colour=colours[0], fig=fig, should_show=False)
    else:  # NON-DEFAULT
        fig = parameter.plot_rper(colour=colours[1], alpha=0.2, fig=fig, should_show=False, linestyle='--')
        fig = parameter.plot_rper_band(colour=colours[1], alpha=1, fig=fig, should_show=False, linestyle='-', show_band=False)
        fig = without.plot_rper_band(colour=colours[0], fig=fig, should_show=False)

    plotter = Plotter(fig)
    if is_default:  # DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    else:  # NON-DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    plotter.set_title(title)
    plotter.save(f'{sim_name}_rper_{fig_name}')
    plotter.show()

if is_rpet:
    fig = None
    if is_default:  # DEFAULT
        fig = parameter.plot_rpet_band(colour=colours[1], fig=fig, should_show=False)
        fig = without.plot_rpet_band(colour=colours[0], fig=fig, should_show=False)
    else:  # NON-DEFAULT
        fig = parameter.plot_rpet(colour=colours[1], alpha=0.2, fig=fig, should_show=False, linestyle='--')
        fig = parameter.plot_rpet_band(colour=colours[1], alpha=1, fig=fig, should_show=False, linestyle='-', show_band=False)
        fig = without.plot_rpet_band(colour=colours[0], fig=fig, should_show=False)

    plotter = Plotter(fig)
    if is_default:  # DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    else:  # NON-DEFAULT
        plotter.legend(labels, lines=[blue['-'], orange['-']])
        plotter.y_limits(0., None)
    plotter.set_title(title)
    plotter.save(f'{sim_name}_rpet_{fig_name}')
    plotter.show()
