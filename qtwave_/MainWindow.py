from qtwave_.MenuBar import MenuBar
from qtwave_.HierarchyWidget.HierarchyWidget import HierarchyWidget
from qtwave_.WaveformWidget.WaveformWidget import WaveformWidget
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
	QMainWindow,
	QSplitter,
)

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("qtwave")
		self.menu_bar = MenuBar(self)
		self._CreateMainLayout()
		self._ConnectSignals()
		self.show()

	def _CreateMainLayout(self):
		main_widget = QSplitter(Qt.Orientation.Horizontal)
		main_widget.setChildrenCollapsible(False)
		self.setCentralWidget(main_widget)

		left_widget = HierarchyWidget()
		main_widget.addWidget(left_widget)

		right_widget = WaveformWidget()
		main_widget.addWidget(right_widget)

	def _ConnectSignals(self):
		pass
