import typing as tp

from src.framework.optimiser.Optimiser import Library, Solver, Optimiser
from src.gui.utils.GroupComboBox import GroupComboBox, GroupItem


class SolverBox(GroupComboBox):

    # constructor
    def __init__(
            self,
            optimiser: Optimiser,
            **kwargs
    ):
        super().__init__(**kwargs)

        # attributes
        self._optimiser = optimiser
        self._elements: tp.List[tp.Optional[tp.Tuple[Library, Solver]]] = []

        # handlers
        self.currentIndexChanged.connect(self._handle_index_change)

        # actions
        self._construct()
        self.setCurrentIndex(1)

    # helper-methods
    def _construct(self):
        self._elements = []

        self.blockSignals(True)
        self.clear()

        library: Library
        for library in self._optimiser.get_libraries():
            group: GroupItem = self.add_group(f'{library.value}')
            self._elements.append(None)

            solver: Solver
            for solver in self._optimiser.get_solvers(library):
                group.add_child(f'{solver.value}')
                self._elements.append((library, solver))
        self.blockSignals(False)

    # handlers
    def _handle_index_change(self, index):
        if index >= 0:
            library, solver = self._elements[index]
            self._optimiser.set(library, solver)
            print(f"gui/SolverBox: Solver set to '{library.value}/{solver.value}'.")
