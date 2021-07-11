import copy
import typing as tp

import numpy as np
from matplotlib import pyplot as plt
from src.framework.graph.Graph import SubGraph
from src.framework.math.matrix.vector import SubVector
from src.framework.math.matrix.vector.Vector import Vector
from src.framework.optimiser.Optimiser import Optimiser


class GraphAnalyser(object):

    @staticmethod
    def plot_error_slice(graph, steps: int = 50):
        assert graph.has_true()
        assert graph.has_pre()

        pre_vector: SubVector = graph.get_pre().to_vector()
        opt_vector: SubVector = graph.to_vector()
        unit: SubVector = Vector(pre_vector.array() - opt_vector.array())

        graph: SubGraph = copy.deepcopy(graph)
        line: tp.List[float] = list(np.linspace(-2, 2, steps + 1))
        error: tp.List[float] = []
        for x in line:
            vector: SubVector = Vector(opt_vector.array() + unit.array() * x)
            graph.from_vector(vector)
            error.append(graph.compute_error())
        plt.plot(line, error)
        plt.show()

    @staticmethod
    def plot_metrics(graph) -> None:
        assert graph.has_metrics()

        optimiser = Optimiser()

        edge_count: tp.List[int] = []
        ate: tp.List[float] = []
        import time

        t = time.time()
        subgraphs: tp.List[SubGraph] = graph.get_subgraphs()
        print(time.time() - t)
        for i, subgraph in enumerate(subgraphs):
            print(i)
            optimised: SubGraph = optimiser.optimise(subgraph)
            ate.append(optimised.compute_rpe_translation())
            edge_count.append(i)
        plt.plot(edge_count, ate)
        plt.show()
