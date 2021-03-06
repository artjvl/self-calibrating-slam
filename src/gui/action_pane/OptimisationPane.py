from PyQt5 import QtWidgets

from src.gui.action_pane.GraphBox import GraphBox
from src.gui.action_pane.LibraryBox import LibraryBox
from src.gui.action_pane.SolverBox import SolverBox
from src.gui.modules.GraphContainer import GraphContainer
from src.gui.modules.OptimisationHandler import OptimisationHandler


class OptimisationPane(QtWidgets.QWidget):

    # constructor
    def __init__(
            self,
            container: GraphContainer,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._container = container,
        self._optimisation_handler = OptimisationHandler(container)

        layout = QtWidgets.QVBoxLayout()

        self.setLayout(layout)

        # graph optimisation
        graph_box = GraphBox(container, self._optimisation_handler, self)
        graph_box_label = QtWidgets.QLabel(graph_box)
        graph_box_label.setText('Choose a graph:')

        layout.addWidget(graph_box_label)
        layout.addWidget(graph_box)

        library_box = LibraryBox(self._optimisation_handler, self)
        library_box_label = QtWidgets.QLabel(graph_box)
        library_box_label.setText('Choose an optimisation library:')

        layout.addWidget(library_box_label)
        layout.addWidget(library_box)

        solver_box = SolverBox(self._optimisation_handler, self)
        solver_box_label = QtWidgets.QLabel(graph_box)
        solver_box_label.setText('Choose a solver:')

        layout.addWidget(solver_box_label)
        layout.addWidget(solver_box)

        button_optimise = QtWidgets.QPushButton(self)
        button_optimise.setText('Optimise graph')
        button_optimise.clicked.connect(self._optimisation_handler.optimise)
        layout.addWidget(button_optimise)
