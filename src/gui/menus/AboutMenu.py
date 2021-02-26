from functools import partial

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from src.gui.menus.Menu import Menu


class AboutMenu(Menu):

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('&About')
        url = QUrl('https://github.com/artjvl/self-calibrating-slam')
        self.add_action(
            menu=self,
            name='Go to GitHub',
            tip='Redirect to source-code on GitHub',
            handler=partial(QDesktopServices.openUrl, url)
        )
