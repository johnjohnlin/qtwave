from PyQt6.QtCore import (
	QAbstractTableModel,
	QModelIndex,
	Qt
)
from qtwave_.Waveform import SignalData
from typing import *

class SignalModel(QAbstractTableModel):
	signals : List[SignalData]

	def __init__(self):
		super().__init__()
		self.signals = list()

	def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
		return len(self.signals)

	def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
		return 2

	def data(self, index: QModelIndex, role = Qt.ItemDataRole.DisplayRole):
		if role != Qt.ItemDataRole.DisplayRole:
			return None
		x = index.column()
		y = index.row()
		signal = self.signals[y]
		if x == 0:
			return signal.signal_name
		elif x == 1:
			return signal.bit_width
		return None

	def headerData(self, x : int, orientation, role = Qt.ItemDataRole.DisplayRole):
		if (
			role != Qt.ItemDataRole.DisplayRole or
			orientation != Qt.Orientation.Horizontal
		):
			return None
		return ["Name", "Width"][x]
