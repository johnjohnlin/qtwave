from PySide6 import QtCore, QtGui, QtWidgets
from waveform import waveformloader

class WaveformModuleModel(QtCore.QAbstractItemModel):
	def __init__(self):
		QtCore.QAbstractItemModel.__init__(self)
		self.wave_ = waveformloader.Waveform("waveform/test_ahb_example.fst")

	def rowCount(self, node_index):
		if node_index.column() > 0:
			return 0
		node = node_index.internalPointer() if node_index.isValid() else self.wave_.root_
		return len(node.module_children_)

	def columnCount(self, node_index):
		return 2

	def index(self, row, column, parent_index):
		if not self.hasIndex(row, column, parent_index):
			return QtCore.QModelIndex()
		parent = parent_index.internalPointer() if parent_index.isValid() else self.wave_.root_
		if row < len(parent.module_children_):
			return self.createIndex(row, column, parent.module_children_[row])
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
			return "Value" if section == 1 else "Type"
		return None

class WaveformSignalModel(QtCore.QAbstractTableModel):
	def __init__(self):
		QtCore.QAbstractTableModel.__init__(self)
		self.signal_list = list()

	def rowCount(self, node_index):
		return len(self.signal_list)

	def columnCount(self, node_index):
		return 2

	def data(self, node_index, role):
		if role == QtCore.Qt.DisplayRole:
			col = node_index.column()
			sig = self.signal_list[node_index.row()]
			if col == 0:
				return sig.name_
			else:
				return sig.signal_data_.nbit_
		return None

	def ResetModel(self, signal_list):
		self.beginResetModel()
		self.signal_list = signal_list
		self.endResetModel()

	def headerData(self, section, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return "Bit" if section == 1 else "Name"
		return None

class SignalListWidget(QtWidgets.QSplitter):
	def __init__(self):
		super().__init__(QtCore.Qt.Orientation.Vertical, childrenCollapsible=False)
		# model
		self.module_tree_model = WaveformModuleModel()
		self.signal_list_model = WaveformSignalModel()

		# module tree view
		self.module_tree_widget = QtWidgets.QTreeView(
			minimumWidth=50,
			model=self.module_tree_model
		)
		self.module_tree_widget.selectionModel().selectionChanged.connect(self.scng)
		self.module_tree_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.module_tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.module_tree_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		# signal table view
		self.signal_list_widget = QtWidgets.QTableView(
			minimumWidth=50,
			model=self.signal_list_model
		)
		self.signal_list_widget.verticalHeader().hide()
		self.signal_list_widget.horizontalHeader().setStretchLastSection(True)
		self.signal_list_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.signal_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.signal_list_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		self.addWidget(self.module_tree_widget)
		self.addWidget(self.signal_list_widget)

	def scng(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
		sig = selected.indexes()[0].internalPointer()
		self.signal_list_model.ResetModel(sig.signal_children_)
