from PyQt5.QtWidgets import QMainWindow, QWidget, QDesktopWidget, QHBoxLayout, QSizePolicy, QVBoxLayout, QMenuBar, \
    QPushButton, QStatusBar

from src.gui.menus import FileMenu, ViewMenu, AboutMenu
from src.gui.modules.GraphContainer import GraphContainer
from src.gui.modules.OptimisationHandler import OptimisationHandler
from src.gui.modules.SimulationHandler import SimulationHandler
from src.gui.viewer.Viewer import Viewer
from src.gui.widgets import BrowserTree, InspectorTree, TerminalText
from src.gui.widgets.SelectBox import SelectBox
from src.gui.widgets.SimulationBox import SimulationBox


class MainWindow(QMainWindow):
    # reference: https://memotut.com/create-a-3d-model-viewer-with-pyqt5-and-pyqtgraph-b3916/
    #            https://github.com/Be4rR/STLViewer

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # window
        self.setGeometry(200, 200, 1400, 1000)
        # self.centre()
        self.setWindowTitle('Graph-Viewer')

        # initialise central widget
        central_widget = QWidget(self)

        # modules
        self._container = GraphContainer()
        self._simulation = SimulationHandler(self._container)
        self._optimisation = OptimisationHandler(self._container)

        # widgets
        self._viewer: Viewer = self._init_viewer(central_widget, self._container)
        self._menubar: QMenuBar = self._init_menubar(self._container, self._viewer)
        self._statusbar: QStatusBar = self.statusBar()

        # layout
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        # left-layout:
        layout.addLayout(
            self._init_create_layout(
                central_widget,
                self._container,
                self._simulation,
                self._optimisation
            )
        )
        # centre-layout:
        layout.addLayout(
            self._init_centre_layout(
                central_widget,
                self._viewer
            )
        )
        # right-layout:
        layout.addLayout(
            self._init_info_layout(
                central_widget,
                self._container,
                self._viewer
            )
        )

        # show
        self.show()

    def __del__(self):
        print('Exiting application...')

    # initialisers
    @staticmethod
    def _init_viewer(
            widget: QWidget,
            container: GraphContainer
    ) -> Viewer:
        # reference: https://pyqtgraph.readthedocs.io/en/latest/
        viewer: Viewer = Viewer(container, widget)
        viewer.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        return viewer

    @staticmethod
    def _init_info_layout(
            widget: QWidget,
            container: GraphContainer,
            viewer: Viewer
    ) -> QVBoxLayout:
        layout = QVBoxLayout()

        # load-button
        button_load = QPushButton(widget)
        button_load.setText('Load file')
        # button_load.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed))
        button_load.clicked.connect(container.load_graph)
        layout.addWidget(button_load)

        # browser/inspector
        inspector: InspectorTree = InspectorTree(widget)
        inspector.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
        browser: BrowserTree = BrowserTree(container, inspector, viewer, widget)
        browser.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))

        layout.addWidget(browser)
        layout.addWidget(inspector)

        return layout

    @staticmethod
    def _init_centre_layout(
            widget: QWidget,
            viewer: Viewer
    ) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(viewer)

        # terminal
        terminal: TerminalText = TerminalText(widget)
        terminal.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum))
        layout.addWidget(terminal)

        return layout

    @staticmethod
    def _init_create_layout(
            widget: QWidget,
            container: GraphContainer,
            simulation: SimulationHandler,
            optimisation: OptimisationHandler
    ) -> QVBoxLayout:
        layout = QVBoxLayout()

        # graph simulation
        simulator_box: SimulationBox = SimulationBox(simulation, widget)
        layout.addWidget(simulator_box)

        button_simulate = QPushButton(widget)
        button_simulate.setText('Simulate graph')
        button_simulate.clicked.connect(simulation.simulate)
        layout.addWidget(button_simulate)

        # graph optimisation
        select_box: SelectBox = SelectBox(container, optimisation, widget)
        layout.addWidget(select_box)

        button_optimise = QPushButton(widget)
        button_optimise.setText('Optimise graph')
        button_optimise.clicked.connect(optimisation.optimise)
        layout.addWidget(button_optimise)

        return layout

    def _init_menubar(
            self,
            container: GraphContainer,
            viewer: Viewer
    ) -> QMenuBar:
        menubar = self.menuBar()
        menubar.addMenu(FileMenu(container, self))
        menubar.addMenu(ViewMenu(container, viewer, self))
        menubar.addMenu(AboutMenu(self))
        return menubar

    # helper-methods: window
    def centre(self):
        # move frame to centre of screen
        frame_geometry = self.frameGeometry()
        centre = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(centre)
        self.move(frame_geometry.topLeft())
