from qtwave_.HierarchyWidget.ModuleHierarchyModel import ModuleHierarchyModel
from PyQt6.QtWidgets import (
	QLabel,
	QTreeView,
	QVBoxLayout,
	QWidget,
)
from PyQt6.QtCore import (
	pyqtSignal,
	QModelIndex,
)
from typing import *

# debug purpose
from qtwave_.Waveform import BuildTestTree, SignalData
root = BuildTestTree()

class ModuleHierarchyWidget(QWidget):
	main_widget : QTreeView
	hierarchy_model : ModuleHierarchyModel
	module_clicked = pyqtSignal(object) # List[SignalData]

	def __init__(self):
		super().__init__()
		self.hierarchy_model = ModuleHierarchyModel()
		self.hierarchy_model.SetRoot(root) # debug purpose
		layout = QVBoxLayout()
		layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout)
		layout.addWidget(QLabel("Module Hierarchy"))
		self.main_widget = QTreeView()
		self.main_widget.setModel(self.hierarchy_model)
		self.main_widget.header().setStretchLastSection(True)
		self.main_widget.clicked.connect(self._HandleClick)
		layout.addWidget(self.main_widget)

	def _HandleClick(self, index : QModelIndex) -> List[SignalData]:
		emitted_signals = self.hierarchy_model.QModelIndexToNode(index).module_data.signals
		self.module_clicked.emit(emitted_signals)
