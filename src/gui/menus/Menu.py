from typing import *

from PyQt5.QtWidgets import QMenu


class Menu(QMenu):

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def add_menu(
            menu: QMenu,
            name: str
    ) -> QMenu:
        sub = menu.addMenu(name)
        return sub

    @staticmethod
    def add_action(
            menu: QMenu,
            name: str,
            handler: Callable,
            tip: Optional[str] = None,
            checked: Optional[bool] = None
    ):
        action = menu.addAction(name)
        action.triggered.connect(handler)
        if tip is not None:
            action.setToolTip(tip)
        if checked is not None:
            action.setCheckable(True)
            action.setChecked(checked)
        return action
