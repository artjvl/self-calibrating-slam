from typing import *

from PyQt5 import QtCore, QtWidgets, QtGui

from src.framework.simulation.ParameterDictTree import ParameterDictTree
from src.gui.modules.SimulationHandler import SimulationHandler, Union

ParameterType = Union[Type[str], Type[int], Type[float], Type[bool]]
Parameter = Union[str, int, float, bool]


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
            parameters: ParameterDictTree,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._parameters: ParameterDictTree = parameters

    def set_parameters(
            self,
            parameters: ParameterDictTree
    ):
        self._parameters = parameters

    def createEditor(
            self,
            parent: QtWidgets.QWidget,
            option: 'QStyleOptionViewItem',
            index: QtCore.QModelIndex
    ) -> Optional[QtWidgets.QWidget]:
        editor = QtWidgets.QLineEdit(parent)

        types: List[ParameterType] = [
            value.get_type() for value in self._parameters.values()
        ]
        validator: QtGui.QValidator = self.validators[types[index.row()]]
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
            simulation_handler: SimulationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._simulation_handler: SimulationHandler = simulation_handler
        self._simulation_handler.signal_update.connect(self._construct_tree)
        self._delegate = ParameterDelegate(self._simulation_handler.get_parameter_tree())
        self._delegate.signal_edit.connect(self._handle_edit)
        self.setItemDelegateForColumn(1, self._delegate)

        # create tree
        self.headerItem().setText(0, 'Parameter')
        self.headerItem().setText(1, 'Value')
        self.setAlternatingRowColors(True)

        self._construct_tree()

    def _handle_edit(
            self,
            index: int
    ):
        value_string: str = self.topLevelItem(index).text(1)
        parameter_tree = self._simulation_handler.get_parameter_tree()
        key = parameter_tree.keys()[index]
        value: Parameter = parameter_tree[key].get_value().get_type()(value_string)
        # write to item
        parameter_tree.set_parameter(key, value)
        print("Changed parameter '{}' to {}".format(key, value))

    def _construct_tree(self):
        self.clear()

        parameters: ParameterDictTree = self._simulation_handler.get_simulation().get_parameter_tree()
        if parameters is not None:
            self._delegate.set_parameters(parameters)
            for key, value in parameters.key_values():
                self._construct_parameter(self, key, value.get_value())
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

    @staticmethod
    def _construct_parameter(
            root: Union[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem],
            key: str,
            value: Union[int, float]
    ) -> QtWidgets.QTreeWidgetItem:
        item = QtWidgets.QTreeWidgetItem(root)
        item.setText(0, '{}'.format(key))
        item.setFont(0, QtGui.QFont('Courier New', 10))
        item.setText(1, '{}'.format(value))
        item.setFont(1, QtGui.QFont('Courier New', 10))
        item.setFlags(int(item.flags()) | QtCore.Qt.ItemIsEditable)
        return item
