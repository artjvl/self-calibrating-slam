import typing as tp

from PyQt5 import QtCore, QtWidgets, QtGui

from src.framework.simulation.ConfigurationSet import Type, Value, ConfigurationSet


class ParameterDelegate(QtWidgets.QItemDelegate):

    signal_edit = QtCore.pyqtSignal(int)

    validators = {
        str: None,
        int: QtGui.QRegExpValidator(QtCore.QRegExp('-?[1-9]\d*')),
        float: QtGui.QRegExpValidator(QtCore.QRegExp('-?^(0.|[1-9]\d*\.?)\d*')),
        bool: QtGui.QRegExpValidator(QtCore.QRegExp('^(True|False|1|0)$')),
    }

    def __init__(
            self,
            parameters: ConfigurationSet,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._parameters: ConfigurationSet = parameters

    def set_parameters(
            self,
            parameters: ConfigurationSet
    ):
        self._parameters = parameters

    def createEditor(
            self,
            parent: QtWidgets.QWidget,
            option: 'QStyleOptionViewItem',
            index: QtCore.QModelIndex
    ) -> tp.Optional[QtWidgets.QWidget]:
        type_: Type = self._parameters.get(index.row()).get_type()
        validator: QtGui.QValidator = self.validators[type_]

        editor = QtWidgets.QLineEdit(parent)
        editor.setValidator(validator)
        return editor

    def setModelData(
            self,
            editor: QtWidgets.QWidget,
            model: QtCore.QAbstractItemModel,
            index: QtCore.QModelIndex
    ) -> None:
        super().setModelData(editor, model, index)
        self.signal_edit.emit(index.row())


class ParameterTree(QtWidgets.QTreeWidget):

    # constructor
    def __init__(
            self,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        # create tree
        self.headerItem().setText(0, 'Parameter')
        self.headerItem().setText(1, 'Value')
        self.setAlternatingRowColors(True)

        # save parameters
        self._parameters: tp.Optional[ConfigurationSet] = None

    def _handle_edit(
            self,
            index: int
    ):
        key: str = self.topLevelItem(index).text(0)
        value: str = self.topLevelItem(index).text(1)
        self._parameters[key] = value
        print(f"Changed '{key}' to '{value}'.")

    def construct_tree(self, parameters: ConfigurationSet):
        # save parameters
        self._parameters = parameters

        # set delegate
        delegate = ParameterDelegate(parameters)
        delegate.signal_edit.connect(self._handle_edit)
        self.setItemDelegateForColumn(1, delegate)

        # fill tree
        self.clear()
        for key, value in parameters.to_dict().items():
            self._construct_parameter(self, key, value.get_value())
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

    @staticmethod
    def _construct_parameter(
            root: tp.Union[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem],
            key: str,
            value: tp.Union[int, float]
    ) -> QtWidgets.QTreeWidgetItem:
        item = QtWidgets.QTreeWidgetItem(root)
        item.setText(0, '{}'.format(key))
        item.setFont(0, QtGui.QFont('Courier New', 10))
        item.setText(1, '{}'.format(value))
        item.setFont(1, QtGui.QFont('Courier New', 10))
        item.setFlags(int(item.flags()) | QtCore.Qt.ItemIsEditable)
        return item
