import time
import typing as tp

import matplotlib.pyplot as plt
import numpy as np
from src.framework.analysis.sim.GraphData import GraphData

if tp.TYPE_CHECKING:
    from src.framework.analysis.sim.GraphData import SubGraphData
    from src.simulation.results.Results import SubResults


class SimulationSet(object):
    _simulations: tp.Dict[str, tp.Tuple['SubResults', tp.List[int], int]]

    def __init__(self):
        self._simulations = {}

    def add(
            self,
            name: str,
            simulation: 'SubResults',
            num_runs: int,
            configs: tp.Any = None
    ) -> None:
        if configs is None:
            configs = [None]
        assert name not in self._simulations
        self._simulations[name] = (simulation, configs, num_runs)

    def run(self) -> None:
        num_sims: int = len(self._simulations)
        for i, name in enumerate(self._simulations.keys()):
            self.run_sim(
                name,
                print_index=f'({i + 1}/{num_sims})'
            )

    def run_sim(
            self,
            sim_name: str,
            print_index: str = '(-/-)'
    ) -> tp.List['SubGraphData']:
        graph_datas: tp.List['SubGraphData'] = []

        simulation, configs, num_mc = self._simulations[sim_name]
        num_configs: int = len(configs)
        num_runs: int = num_configs * num_mc
        durations: tp.List[float] = []
        t_sim: float = time.time()

        for j, config in enumerate(configs):
            config_str: str = f'{j + 1}'
            if isinstance(config, int) or isinstance(config, str):
                config_str = f'{config}'

            graph_data: 'SubGraphData' = GraphData()
            for k in range(num_mc):
                print(
                    f"Simulating {simulation.__class__.__name__} '{sim_name}' {print_index}: config {config_str} of {len(configs)},  Monte Carlo run {k + 1}/{num_mc}..."
                )
                simulation.set_sensor_seed(k)
                simulation.set_config(config)
                t_run: float = time.time()
                graph_data.add_graph(simulation.run())
                t_current: float = time.time()
                duration: float = t_current - t_run

                count: int = j * num_mc + k + 1
                durations.append(duration)
                avg_duration: float = float(np.mean(duration))
                num_runs_left: int = num_runs - count
                print(
                    f"Run duration: {duration:.2f} (total: {t_current - t_sim:.2f}, {count} runs); Estimated time left: {num_runs_left * avg_duration:.2f} s ({num_runs_left} runs)"
                )

            title: str = f'{sim_name}-{config_str}-{num_mc}'
            graph_data.save(title)
            graph_datas.append(graph_data)

            fig = graph_data.plot_cost(show=False)
            fig.suptitle(title)
            fig.show()

            fig: plt.Figure = graph_data.plot_ate(show=False)
            fig.suptitle(title)
            fig.show()

            for parameter_name in graph_data.get_parameters():
                fig: plt.Figure = graph_data.plot_parameter(parameter_name, show=False)
                fig.suptitle(title)
                fig.show()
            print(f'{title}: {np.mean(graph_data._metrics.mean(graph_data._ATE))}')
        return graph_datas
