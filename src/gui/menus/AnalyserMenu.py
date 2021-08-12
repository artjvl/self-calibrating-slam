from framework.graph.GraphAnalyser import GraphAnalyser

from src.gui.menus.Menu import Menu


class AnalyserMenu(Menu):

    # constructor
    def __init__(
            self,
            analyser: GraphAnalyser,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.setTitle('Analyser')
        self.add_action(
            menu=self,
            name='Reset plots',
            tip='Resets the analyser plots',
            handler=analyser.clear
        )
