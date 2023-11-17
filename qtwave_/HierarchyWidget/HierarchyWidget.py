from qtwave_.HierarchyWidget.ModuleHierarchyWidget import ModuleHierarchyWidget
from qtwave_.HierarchyWidget.SignalWidget import SignalWidget
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter

class HierarchyWidget(QSplitter):
	module_widget : ModuleHierarchyWidget
	signal_widget : SignalWidget

	def __init__(self):
		self._InitSuper()
		self._InitLayout()
		self._ConnectSignals()

	def _InitSuper(self):
		super().__init__(Qt.Orientation.Vertical)
		self.setChildrenCollapsible(False)

	def _InitLayout(self):
		self.module_widget = ModuleHierarchyWidget()
		self.signal_widget = SignalWidget()
		self.addWidget(self.module_widget)
		self.addWidget(self.signal_widget)

	def _ConnectSignals(self):
		self.module_widget.module_clicked.connect(
			self.signal_widget.UpdateModuleSignals
		)
