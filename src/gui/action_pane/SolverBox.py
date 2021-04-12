from typing import *

from src.gui.action_pane.UpdateBox import UpdateBox
from src.gui.modules.OptimisationHandler import OptimisationHandler


class SolverBox(UpdateBox):

    # constructor
    def __init__(
            self,
            optimisation_handler: OptimisationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._optimisation_handler = optimisation_handler
        self._optimisation_handler.signal_update.connect(lambda: self._update_box(self._get_texts()))
        self._update_box(self._get_texts())
        self.currentIndexChanged.connect(self._handle_index_change)

    # helper-methods
    def _get_texts(self) -> List[str]:
        return [solver.value for solver in self._optimisation_handler.get_solvers()]

    # handlers
    def _handle_index_change(self, index):
        if index >= 0:
            solvers = self._optimisation_handler.get_solvers()
            self._optimisation_handler.set_solver(solvers[index])
