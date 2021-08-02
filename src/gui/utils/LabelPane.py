from PyQt5 import QtWidgets


class LabelPane(QtWidgets.QWidget):

    # constructor
    def __init__(
            self,
            widget: QtWidgets.QWidget,
            label_string: str,
            **kwargs
    ):
        super().__init__(**kwargs)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        label = QtWidgets.QLabel(widget)
        label.setText(label_string)

        layout.addWidget(label)
        layout.addWidget(widget)
