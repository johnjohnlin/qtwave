from PySide6 import QtCore, QtGui, QtWidgets
from waveform import waveformloader

class WaveformModuleModel(QtCore.QAbstractItemModel):
	def __init__(self):
		QtCore.QAbstractItemModel.__init__(self)

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

	def ResetModel(self, wave):
		self.beginResetModel()
		self.wave_ = wave
		self.endResetModel()

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

class WaveformSignalFilteredModel(QtCore.QSortFilterProxyModel):
	def __init__(self):
		QtCore.QSortFilterProxyModel.__init__(self)

class SignalListWidget(QtWidgets.QSplitter):
	signal_double_clicked_signal = QtCore.Signal(str, waveformloader.SignalData)
	file_loaded_signal = QtCore.Signal(waveformloader.Waveform)
	def __init__(self):
		super().__init__(QtCore.Qt.Orientation.Vertical, childrenCollapsible=False)
		# model
		self.module_tree_model = WaveformModuleModel()
		self.signal_list_model = WaveformSignalModel()
		self.signal_filter_model = WaveformSignalFilteredModel()
		self.signal_filter_model.setSourceModel(self.signal_list_model)

		# module tree view
		self.module_tree_widget = QtWidgets.QTreeView(
			minimumWidth=50,
			model=self.module_tree_model
		)
		self.module_tree_widget.selectionModel().selectionChanged.connect(self.selectionChangedCallback)
		self.module_tree_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.module_tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.module_tree_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		# signal table view
		self.signal_list_widget = QtWidgets.QTableView(
			minimumWidth=50,
			model=self.signal_filter_model
		)
		self.signal_list_widget.verticalHeader().hide()
		self.signal_list_widget.horizontalHeader().setStretchLastSection(True)
		self.signal_list_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.signal_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.signal_list_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		self.signal_list_widget.doubleClicked.connect(self.doubleClickedCallback)
		# filter text input
		self.filter_widget = QtWidgets.QWidget()
		self.filter_layout = QtWidgets.QHBoxLayout()
		self.filter_label_widget = QtWidgets.QLabel(self)
		self.filter_label_widget.setText("Filter: ")
		self.filter_input_widget = QtWidgets.QLineEdit(
			minimumWidth = 50
		)
		self.filter_input_widget.textChanged.connect(self.signal_filter_model.setFilterFixedString)
		self.filter_layout.addWidget(self.filter_label_widget)
		self.filter_layout.addWidget(self.filter_input_widget)
		self.filter_widget.setLayout(self.filter_layout)

		# add widget
		self.addWidget(self.module_tree_widget)
		self.addWidget(self.signal_list_widget)
		self.addWidget(self.filter_widget)
		self.loadFile("waveform/test_ahb_example.fst")

	def selectionChangedCallback(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
		sig = selected.indexes()[0].internalPointer()
		self.signal_list_model.ResetModel(sig.signal_children_)

	def doubleClickedCallback(self, idx: QtCore.QModelIndex):
		i = idx.row()
		name = self.signal_list_model.signal_list[i].name_
		sig = self.signal_list_model.signal_list[i].signal_data_
		self.signal_double_clicked_signal.emit(name, sig)

	def loadFile(self, fname):
		wave = waveformloader.Waveform(fname)
		self.signal_list_model.ResetModel(list())
		self.module_tree_model.ResetModel(wave)
		self.file_loaded_signal.emit(wave)