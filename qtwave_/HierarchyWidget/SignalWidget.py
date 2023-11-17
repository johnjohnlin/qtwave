from qtwave_.HierarchyWidget.SignalModel import SignalModel, SignalData
from PyQt6.QtWidgets import (
	QLabel,
	QTableView,
	QVBoxLayout,
	QWidget,
)
from typing import *

class SignalWidget(QWidget):
	main_widget : QTableView
	signal_model : SignalModel

	def __init__(self):
		super().__init__()
		self.signal_model = SignalModel()
		layout = QVBoxLayout()
		layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout)
		layout.addWidget(QLabel("Module Signals"))
		self.main_widget = QTableView()
		self.main_widget.setModel(self.signal_model)
		self.main_widget.horizontalHeader().setStretchLastSection(True)
		self.main_widget.verticalHeader().hide()
		self.main_widget.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
		layout.addWidget(self.main_widget)

	def UpdateModuleSignals(self, signals : List[SignalData]):
		self.signal_model.beginResetModel()
		self.signal_model.signals = signals
		self.signal_model.endResetModel()
