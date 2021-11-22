import subprocess
import typing as tp
from enum import Enum
from pathlib import Path

from src.definitions import get_project_root
from src.framework.graph.GraphParser import GraphParser

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubGraph

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
    def __init__(
            self,
            library: Library = Library.CHOLMOD,
            solver: Solver = Solver.GN
    ):
        self._library = library
        self._solver = solver

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

    @classmethod
    def get_libraries(cls) -> tp.List[Library]:
        return list(cls.solvers.keys())

    @classmethod
    def get_solvers(
            cls,
            library: Library
    ) -> tp.List[Solver]:
        return list(cls.solvers[library].keys())

    @classmethod
    def get_solver_string(
            cls,
            library: Library,
            solver: Solver
    ) -> str:
        return cls.solvers[library][solver]

    def instance_optimise(
            self,
            graph,
            should_print: bool = False,
            compute_marginals: bool = False
    ) -> tp.Optional['SubGraph']:
        return self.optimise(
            graph,
            self._library,
            self._solver,
            should_print=should_print,
            compute_marginals=compute_marginals
        )

    @classmethod
    def optimise(
            cls,
            graph: 'SubGraph',
            library: Library = Library.CHOLMOD,
            solver: Solver = Solver.GN,
            should_print: bool = False,
            compute_marginals: bool = False
    ) -> tp.Optional['SubGraph']:
        root: Path = get_project_root()
        relative_to: str = 'graphs/temp'
        GraphParser.save_path_folder(graph, relative_to, 'before', should_print=should_print)

        path_g2o_bin: Path = (root / 'g2o/bin/g2o_d').resolve()
        path_input: Path = (root / (relative_to + '/before.g2o')).resolve()
        path_output: Path = (root / (relative_to + '/after.g2o')).resolve()
        path_summary: Path = (root / (relative_to + '/summary.g2o')).resolve()
        path_output.unlink(missing_ok=True)

        solver_string: str = cls.get_solver_string(library, solver)
        commands: tp.List[str] = [
            str(path_g2o_bin),
            '-solver', solver_string,
            '-o', str(path_output)
        ]
        if should_print:
            commands.append('-v')
        if compute_marginals:
            commands.append('-computeMarginals')
        commands.append(str(path_input))

        if should_print:
            print(f"framework/Optimiser: Issuing command '{' '.join(commands)}'")
            process = subprocess.run(commands)
        else:
            process = subprocess.run(commands, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        if path_output.exists():
            solution: 'SubGraph' = GraphParser.load(path_output, reference=graph, should_print=should_print)
            # graph.copy_attributes_to(solution)
            return solution
        return None
