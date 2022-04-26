#!/usr/bin/env python
from PySide6 import QtCore, QtGui, QtWidgets
import sys
from waveform import waveformloader
import numpy as np


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

def TraverseMenu(parent, menu_dict):
	for k, v in menu_dict.items():
		if isinstance(v, dict):
			# recursive menu
			menu = QtWidgets.QMenu(k, parent)
			TraverseMenu(menu, v)
			parent.addMenu(menu)
		else:
			# separator or item
			if k.startswith("-"):
				parent.addSeparator()
			else:
				action = QtGui.QAction(k, parent)
				parent.addAction(action)
				action.triggered.connect(v)

class QtWave(QtWidgets.QMainWindow):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.menu_bar = self.CreateMenuBar()
		self.status_bar = self.CreateStatusBar()
		self.tool_bar = None
		self.central_widget = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, childrenCollapsible=False)
		self.waveform_model = QtWidgets.QGraphicsScene()
		self.waveform_widget = QtWidgets.QGraphicsView(
			self.waveform_model,
			minimumWidth=50
		)
		self.waveform_model.setBackgroundBrush(QtCore.Qt.black)
		self.signal_list_model = QtWaveModel()
		self.signal_list_widget = QtWidgets.QTreeView(
			headerHidden=False,
			minimumWidth=50,
			model=self.signal_list_model
		)
		self.AddTestLine()
		self.InitModel()
		self.central_widget.addWidget(self.signal_list_widget)
		self.central_widget.addWidget(self.waveform_widget)
		self.setCentralWidget(self.central_widget)
		self.setMenuBar(self.menu_bar)
		self.setStatusBar(self.status_bar)
		# self.setToolBar(self.menu_bar)

	def InitModel(self):
		pass

	def AddTestLine(self):
		HEIGHT = 20
		HSTRIDE = 30
		XRANGE = 1000
		ofs = 0
		timepoints = np.arange(XRANGE)*1400
		for k, v in self.signal_list_model.wave_.signal_data_.items():
			if v.nbit_ == 6:
				idx, tps, data01, dataxz = v.GetValuesFromTimepoints(timepoints)
				line = QtWidgets.QGraphicsLineItem(0, ofs, XRANGE, ofs)
				line.setPen(QtGui.QPen(QtCore.Qt.green))
				self.waveform_model.addItem(line)
				line = QtWidgets.QGraphicsLineItem(0, ofs+HEIGHT, XRANGE, ofs+HEIGHT)
				line.setPen(QtGui.QPen(QtCore.Qt.green))
				self.waveform_model.addItem(line)
				for i in range(idx.size):
					line = QtWidgets.QGraphicsLineItem(idx[i], ofs, idx[i], ofs+HEIGHT)
					line.setPen(QtGui.QPen(QtCore.Qt.green))
					self.waveform_model.addItem(line)
			ofs += HSTRIDE

	def CreateMenuBar(self):
		menu_bar = QtWidgets.QMenuBar(self)
		menu_items = {
			"&File": {
				"&Open": lambda: self.status_bar.showMessage("1"),
				"&Save": lambda: self.status_bar.showMessage("2"),
				"&Exit": lambda: self.status_bar.showMessage("3"),
			},
			"&Edit": {
				"&Copy": lambda: self.status_bar.showMessage("4"),
				"-": None,
				"&Find and Replace": {
					"&Find": lambda: self.status_bar.showMessage("5"),
					"&Replace": lambda: self.status_bar.showMessage("6"),
				},
			},
			"&Help": {
				"&About": lambda: self.status_bar.showMessage("7"),
			},
		}
		TraverseMenu(menu_bar, menu_items)
		return menu_bar

	def CreateStatusBar(self):
		status_bar = QtWidgets.QStatusBar()
		return status_bar

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	qtwave = QtWave()
	qtwave.show()
	sys.exit(app.exec())