import subprocess
from enum import Enum
from pathlib import Path
from typing import *

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
        self._graph: Optional[Graph] = None
        self._library = Library.CHOLMOD
        self._solver = Solver.GN

    # public methods
    def set_graph(self, graph: Optional[Graph]):
        self._graph = graph

    def get_graph(self) -> Optional[Graph]:
        return self._graph

    def set_library(self, library: Library):
        self._library = library

    def set_solver(self, solver: Solver):
        assert solver in self.solvers[self._library]
        self._solver = solver

    def get_libraries(self) -> List[Library]:
        return list(self.solvers.keys())

    def get_solvers(self) -> List[Solver]:
        return list(self.solvers[self._library].keys())

    def _get_solver_string(self) -> str:
        return self.solvers[self._library][self._solver]

    def optimise(self) -> Graph:
        root: Path = get_project_root()
        relative_to: str = 'graphs/temp'
        GraphParser.save_path_folder(self.get_graph(), relative_to, 'before')

        path_g2o_bin: Path = (root / 'g2o/bin/g2o_d').resolve()
        path_input: Path = (root / (relative_to + '/before.g2o')).resolve()
        path_output: Path = (root / (relative_to + '/after.g2o')).resolve()
        path_summary: Path = (root / (relative_to + '/summary.g2o')).resolve()

        solver_string: str = self._get_solver_string()
        process = subprocess.run([
            str(path_g2o_bin),
            '-solver', solver_string,
            '-o', str(path_output),
            '-v',
            '-summary', str(path_summary),
            str(path_input)
        ])

        graph: Graph = GraphParser.load(path_output)
        return graph
