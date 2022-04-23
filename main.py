#!/usr/bin/env python
from PySide6 import QtCore, QtGui, QtWidgets
import sys

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
		line = QtWidgets.QGraphicsLineItem(0, 0, 100, 100)
		line.setPen(QtGui.QPen(QtCore.Qt.green))
		self.waveform_model.setBackgroundBrush(QtCore.Qt.black)
		self.waveform_model.addItem(line)
		self.signal_list_model = QtGui.QStandardItemModel()
		self.signal_list_widget = QtWidgets.QTreeView(
			headerHidden=True,
			minimumWidth=50,
			model=self.signal_list_model
		)
		self.InitModel()
		self.central_widget.addWidget(self.signal_list_widget)
		self.central_widget.addWidget(self.waveform_widget)
		self.setCentralWidget(self.central_widget)
		self.setMenuBar(self.menu_bar)
		self.setStatusBar(self.status_bar)
		# self.setToolBar(self.menu_bar)

	def InitModel(self):
		root = self.signal_list_model.invisibleRootItem()
		#root.appendRow("1")
		#root.appendRow("3")
		def F(s):
			c1 = QtGui.QStandardItem(s)
			c2 = QtGui.QStandardItem(s*2)
			c2.setEditable(False)
			return c1, c2
		a, b, c = [F(x) for x in "abc"]
		root.appendRow(a)
		root.appendRow(b)
		b[0].appendRow(c)

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