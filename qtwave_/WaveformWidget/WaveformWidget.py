from qtwave_.WaveformWidget.WaveformGraphWidget import WaveformGraphWidget
from qtwave_.WaveformWidget.WaveformListWidget import WaveformListWidget
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter
from typing import *

class WaveformWidget(QSplitter):
	graph_widget : WaveformGraphWidget
	list_widget : WaveformListWidget

	def __init__(self):
		self._InitSuper()
		self._InitLayout()
		self._ConnectSignals()

	def _InitSuper(self):
		super().__init__(Qt.Orientation.Horizontal)
		self.setChildrenCollapsible(False)

	def _InitLayout(self):
		self.list_widget = WaveformListWidget()
		self.graph_widget = WaveformGraphWidget()
		self.addWidget(self.list_widget)
		self.addWidget(self.graph_widget)

	def _ConnectSignals(self):
		pass
