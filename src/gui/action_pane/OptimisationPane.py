from PyQt5 import QtWidgets
from src.gui.action_pane.GraphBox import GraphBox
from src.gui.action_pane.HistoryCheckbox import HistoryCheckbox
from src.gui.action_pane.SolverBox import SolverBox
from src.gui.modules.OptimisationHandler import OptimisationHandler
from src.gui.modules.TreeNode import TopTreeNode
from src.gui.utils.LabelPane import LabelPane


class OptimisationPane(QtWidgets.QWidget):

    _tree: TopTreeNode
    _optimisation_handler: OptimisationHandler

    # constructor
    def __init__(
            self,
            tree: TopTreeNode,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._tree = tree
        self._optimisation_handler = OptimisationHandler(tree)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # graph-selection box
        graph_box = GraphBox(tree, self._optimisation_handler, self)
        history_checkbox = HistoryCheckbox(self._optimisation_handler)
        layout.addWidget(LabelPane(graph_box, 'Choose a graph:'))
        layout.addWidget(history_checkbox)

        # solver box
        solver_box = SolverBox(self._optimisation_handler.get_optimiser(), self)
        layout.addWidget(LabelPane(solver_box, 'Choose a Library/Solver:'))

        # optimise button
        self._button_optimise = QtWidgets.QPushButton(self)
        self._button_optimise.setText('Optimise graph')
        self._button_optimise.clicked.connect(self._optimisation_handler.optimise)
        self._button_optimise.setEnabled(False)
        self._optimisation_handler.signal_update.connect(self._handle_graph_selection_update)
        layout.addWidget(self._button_optimise)

    def _handle_graph_selection_update(self, signal: int):
        self._button_optimise.setEnabled(True if signal >= 0 else False)
