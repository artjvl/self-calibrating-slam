from PyQt5.QtWidgets import QComboBox

from src.gui.modules.OptimisationHandler import OptimisationHandler


class LibraryBox(QComboBox):

    # constructor
    def __init__(
            self,
            optimisation_handler: OptimisationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._optimisation_handler = optimisation_handler
        self._libraries = self._optimisation_handler.get_libraries()
        for library in self._libraries:
            self.addItem(library.value)
        self.currentIndexChanged.connect(self._handle_index_change)

    # handlers
    def _handle_index_change(self, index):
        self._optimisation_handler.set_library(self._libraries[index])
