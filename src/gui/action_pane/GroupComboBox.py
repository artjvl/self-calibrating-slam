from PyQt5 import QtCore, QtWidgets, QtGui

GroupRole = QtCore.Qt.UserRole

# reference: https://stackoverflow.com/questions/57437204/qcombobox-add-bold-parent-items

class GroupDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if not index.data(GroupRole):
            option.text = '    ' + option.text


class GroupItem(QtGui.QStandardItem):
    def __init__(self, text):
        super(GroupItem, self).__init__(text)
        self.setData(True, GroupRole)
        self._number_of_children = 0
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsSelectable)

    def add_child(self, text):
        item = QtGui.QStandardItem(text)
        item.setData(False, GroupRole)
        self._number_of_children += 1
        self.model().insertRow(self.row() + self._number_of_children, item)
        return item


class GroupComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(QtGui.QStandardItemModel(self))
        delegate = GroupDelegate(self)
        self.setItemDelegate(delegate)

    def add_group(self, text):
        item = GroupItem(text)
        self.model().appendRow(item)
        return item

    def add_child(self, text):
        item = QtGui.QStandardItem(text)
        item.setData(True, GroupRole)
        self.model().appendRow(item)
