from typing import *

from PyQt5 import QtCore, QtWidgets, QtGui

from src.framework.simulation.ParameterDictTree import ParameterDictTree
from src.gui.modules.SimulationHandler import SimulationHandler, Union

ParameterTypes = List[Union[Type[str], Type[int], Type[float], Type[bool]]]


class ParameterDelegate(QtWidgets.QItemDelegate):
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
        self._types: ParameterTypes = self._parse_parameters(parameters)

    def set_parameters(
            self,
            parameters: ParameterDictTree
    ):
        types: ParameterTypes = self._parse_parameters(parameters)
        self._types = types

    @staticmethod
    def _parse_parameters(
            parameters: ParameterDictTree
    ) -> ParameterTypes:
        # list type: editor is indexed per row
        types: ParameterTypes = []
        for value in parameters.values():
            types.append(value.get_type())
        return types

    def createEditor(
            self,
            parent: QtWidgets.QWidget,
            option: 'QStyleOptionViewItem',
            index: QtCore.QModelIndex
    ) -> Optional[QtWidgets.QWidget]:
        editor = QtWidgets.QLineEdit(parent)
        validator: QtGui.QValidator = self.validators[self._types[index.row()]]
        editor.setValidator(validator)
        return editor


class ParameterTree(QtWidgets.QTreeWidget):

    # constructor
    def __init__(
            self,
            simulation: SimulationHandler,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._simulation_handler: SimulationHandler = simulation
        self._simulation_handler.signal_update.connect(self._construct_tree)

        # create tree
        self.headerItem().setText(0, 'Parameter')
        self.headerItem().setText(1, 'Value')
        self.setAlternatingRowColors(True)

        self._construct_tree()

    def _handle_edit(
            self,
            editor: QtWidgets.QWidget,
            hint
    ):

        print('closed editor')

    def _construct_tree(self):
        self.clear()

        parameters: ParameterDictTree = self._simulation_handler.get_simulation().get_parameter_tree()
        if parameters is not None:
            self.setItemDelegateForColumn(1, ParameterDelegate(parameters))
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
        # item.setData(1, QtCore.Qt.EditRole, value)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        return item
