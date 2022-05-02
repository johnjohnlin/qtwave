from PySide6 import QtCore, QtGui, QtWidgets
from waveform import waveformloader

# show the signal list, TODO: the name sucks
class QtWaveModel(QtCore.QAbstractItemModel):
	def __init__(self):
		QtCore.QAbstractItemModel.__init__(self)
		self.wave_ = waveformloader.Waveform("waveform/test_ahb_example.fst")

	def rowCount(self, node_index):
		if node_index.column() > 0:
			return 0
		node = node_index.internalPointer() if node_index.isValid() else self.wave_.root_
		return len(node.children_)

	def columnCount(self, node_index):
		return 2

	def index(self, row, column, parent_index):
		if not self.hasIndex(row, column, parent_index):
			return QtCore.QModelIndex()
		parent = parent_index.internalPointer() if parent_index.isValid() else self.wave_.root_
		if row < len(parent.children_):
			return self.createIndex(row, column, parent.children_[row])
		else:
			return QtCore.QModelIndex()

	def parent(self, node_index):
		if node_index.isValid():
			parent = node_index.internalPointer().parent_
			if not parent.is_root_:
				return self.createIndex(parent.row_, 0, parent)
		return QtCore.QModelIndex()

	def data(self, node_index, role):
		if node_index.isValid() and role == QtCore.Qt.DisplayRole:
			node = node_index.internalPointer()
			if node_index.column() == 0:
				data = node.name_
			else:
				if node.hier_type_ == 0:
					data = f"module ({node.secondary_type_})"
				else:
					data = str(node.signal_data_[0][1])
			return data
		return None

	def headerData(self, section, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return "Value" if section == 1 else "Name"
		return None
