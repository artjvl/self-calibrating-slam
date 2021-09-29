import time
import typing as tp

import matplotlib.pyplot as plt
import numpy as np
from src.framework.analysis.AnalysisSet import AnalysisSet

if tp.TYPE_CHECKING:
    from src.framework.analysis.AnalysisSet import SubAnalysisSet
    from src.framework.simulation.BiSimulation import SubBiSimulation


class SimulationSet(object):
    _simulations: tp.Dict[str, tp.Tuple['SubBiSimulation', tp.List[int], int]]

    def __init__(self):
        self._simulations = {}

    def add(
            self,
            name: str,
            simulation: 'SubBiSimulation',
            configs: tp.List[int],
            num_runs: int
    ) -> None:
        assert name not in self._simulations
        self._simulations[name] = (simulation, configs, num_runs)

    def run(self) -> None:
        num_sims: int = len(self._simulations)
        for i, name in enumerate(self._simulations.keys()):
            simulation, configs, num_mc = self._simulations[name]

            num_configs: int = len(configs)
            num_runs: int = num_configs * num_mc
            durations: tp.List[float] = []
            t_sim: float = time.time()

            for j, config in enumerate(configs):
                analysis: 'SubAnalysisSet' = AnalysisSet()
                for k in range(num_mc):
                    print(
                        f"Simulating {simulation.__class__.__name__} '{name}' ({i + 1}/{num_sims}): config {config} of {configs},  Monte Carlo run {k + 1}/{num_mc}..."
                    )
                    simulation.set_sensor_seed(k)
                    simulation.set_config(config)
                    t_run: float = time.time()
                    analysis.add_graph(simulation.run())
                    t_current: float = time.time()
                    duration: float = t_current - t_run

                    count: int = j * num_mc + k + 1
                    durations.append(duration)
                    avg_duration: float = float(np.mean(duration))
                    num_runs_left: int = num_runs - count
                    print(
                        f"Run duration: {duration:.2f} (total: {t_current - t_sim:.2f}, {count} runs); Estimated time left: {num_runs_left * avg_duration:.2f} s ({num_runs_left} runs)"
                    )

                title: str = f'{name}-{config}-{num_mc}'
                analysis.save(title)

                fig: plt.Figure = analysis.plot_ate(should_show=False)
                fig.suptitle(title)
                fig.show()

                fig = analysis.plot_error(should_show=False)
                fig.suptitle(title)
                fig.show()
