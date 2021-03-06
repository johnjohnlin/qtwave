#!/usr/bin/env python
from PySide6 import QtCore, QtGui, QtWidgets
import sys
import numpy as np
import WaveformWidget
import ModuleWidget

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
		# Toolbar widgets
		self.menu_bar = self.CreateMenuBar()
		self.status_bar = self.CreateStatusBar()
		# self.tool_bar = None
		# Left and right widgets
		self.module_widget = ModuleWidget.SignalListWidget()
		self.waveform_widget = WaveformWidget.WaveformWidget()
		# Central Widget
		self.central_widget = QtWidgets.QSplitter()
		self.central_widget.addWidget(self.module_widget)
		self.central_widget.addWidget(self.waveform_widget)
		self.setCentralWidget(self.central_widget)
		self.setMenuBar(self.menu_bar)
		self.setStatusBar(self.status_bar)
		# self.setToolBar(self.menu_bar)
		self.module_widget.file_loaded_signal.connect(lambda wave: self.waveform_widget.setMaxTime(wave.max_timepoint_))
		self.module_widget.signal_double_clicked_signal.connect(self.waveform_widget.addSignal)
		self.module_widget.loadFile("waveform/test_ahb_example.fst")

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
