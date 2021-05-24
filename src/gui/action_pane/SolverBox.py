import typing as tp

from src.framework.optimiser.Optimiser import Optimiser, Library, Solver
from src.gui.action_pane.GroupUpdateComboBox import GroupComboBox, GroupItem


class SolverBox(GroupComboBox):

    # constructor
    def __init__(
            self,
            optimiser: Optimiser,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._optimiser = optimiser
        self._solvers: tp.List[tp.Optional[tp.Tuple[Library, Solver]]] = []
        self._construct_box()
        self.currentIndexChanged.connect(self._handle_index_change)

    # helper-methods
    def _construct_box(self):
        library: Library
        for library in self._optimiser.get_libraries():
            self._solvers.append(None)
            group: GroupItem = self.add_group(f'{library.value}')
            for solver in self._optimiser.get_solvers(library):
                self._solvers.append((library, solver))
                group.add_child(f'{solver.value}')
        self.setCurrentIndex(1)

    # handlers
    def _handle_index_change(self, index):
        if index >= 0:
            library, solver = self._solvers[index]
            self._optimiser.set(library, solver)
            print(f"gui/SolverBox: Solver set to '{library.value}/{solver.value}'.")
