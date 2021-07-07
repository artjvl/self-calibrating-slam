import subprocess
import typing as tp
from enum import Enum
from pathlib import Path

from src.definitions import get_project_root
from src.framework.graph.Graph import Graph
from src.framework.graph.GraphParser import GraphParser


class Library(Enum):
    CHOLMOD = 'CHOLMOD'
    CSPARSE = 'CSparse'
    DENSE = 'Dense'
    EIGEN = 'Eigen'
    PCG = 'PCG'


class Solver(Enum):
    GN = 'Gauss-Newton'
    LM = 'Levenberg-Marquardt'
    DL = 'Dogleg'


class Optimiser(object):

    solvers = {
        Library.CHOLMOD: {
            Solver.GN: 'gn_var_cholmod',
            Solver.LM: 'lm_var_cholmod',
            Solver.DL: 'dl_var_cholmod'
        },
        Library.CSPARSE: {
            Solver.GN: 'gn_var_csparse',
            Solver.LM: 'lm_var_csparse',
            Solver.DL: 'dl_var_csparse'
        },
        Library.DENSE: {
            Solver.GN: 'gn_dense',
            Solver.LM: 'lm_dense'
        },
        Library.EIGEN: {
            Solver.GN: 'gn_var',
            Solver.LM: 'lm_var',
            Solver.DL: 'dl_var'
        },
        Library.PCG: {
            Solver.GN: 'gn_pcg',
            Solver.LM: 'lm_pcg'
        }
    }

    # constructor
    def __init__(self):
        self._graph: tp.Optional[Graph] = None
        self._library = Library.CHOLMOD
        self._solver = Solver.GN

    # graph
    def set_graph(self, graph: tp.Optional[Graph]):
        self._graph = graph

    def get_graph(self) -> tp.Optional[Graph]:
        return self._graph

    # solver
    def set(
            self,
            library: Library,
            solver: Solver
    ):
        self.set_library(library)
        self.set_solver(solver)

    def set_library(self, library: Library):
        self._library = library

    def get_library(self) -> Library:
        return self._library

    def set_solver(self, solver: Solver):
        assert solver in self.solvers[self._library]
        self._solver = solver

    def get_solver(self) -> Solver:
        return self._solver

    def get_libraries(self) -> tp.List[Library]:
        return list(self.solvers.keys())

    def get_solvers(
            self,
            library: tp.Optional[Library] = None
    ) -> tp.List[Solver]:
        if library is None:
            library = self._library
        return list(self.solvers[library].keys())

    def get_solver_string(self) -> str:
        return self.solvers[self._library][self._solver]

    def optimise(self) -> Graph:
        root: Path = get_project_root()
        relative_to: str = 'graphs/temp'
        GraphParser.save_path_folder(self._graph, relative_to, 'before')

        path_g2o_bin: Path = (root / 'g2o/bin/g2o_d').resolve()
        path_input: Path = (root / (relative_to + '/before.g2o')).resolve()
        path_output: Path = (root / (relative_to + '/after.g2o')).resolve()
        path_summary: Path = (root / (relative_to + '/summary.g2o')).resolve()

        solver_string: str = self.get_solver_string()
        commands: tp.List[str] = [
            str(path_g2o_bin),
            '-solver', solver_string,
            '-o', str(path_output),
            '-v',
            # '-summary', str(path_summary),
            '-computeMarginals',
            str(path_input)
        ]
        print(f"framework/Optimiser: Issuing command '{' '.join(commands)}'")
        process = subprocess.run(commands)

        graph: Graph = GraphParser.load(path_output)
        graph.assign_pre(self._graph)
        return graph
