import subprocess
from enum import Enum
from pathlib import Path
from typing import *

from src.definitions import get_project_root
from src.framework.graph.Graph import Graph


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
        assert graph.is_uncertain()
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
        path_graphs: Path = (root / 'graphs').resolve()
        path_g2o_bin: Path = (root / 'g2o/bin/g2o').resolve()

        # path to input file
        path_input: Path = (path_graphs / 'temp/before.g2o').resolve()
        self.get_graph().save(path_input)

        # path to output file
        path_output: Path = (path_graphs / 'temp/after.g2o').resolve()

        # solver
        solver_string: str = self._get_solver_string()

        # starts g2o optimiser
        process = subprocess.run([
            str(path_g2o_bin),
            '-solver', solver_string,
            '-o', str(path_output),
            str(path_input)
        ])

        optimised = Graph()
        optimised.load(path_output)
        return optimised
