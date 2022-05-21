from PySide6 import QtCore, QtGui, QtWidgets
from Setting import GetSetting
from WaveformModel import WaveformModel
from WaveformDrawingWidget import WaveformDrawingWidget

class WaveformWidget(QtWidgets.QSplitter):
	def __init__(self):
		super().__init__(QtCore.Qt.Orientation.Horizontal, childrenCollapsible=False)
		self.setting = GetSetting()
		self.model = WaveformModel()
		self.name_widget = self.CreateWaveformNameValueWidget(self.model.proxy_list_model)
		self.drawing_widget = self.CreateWaveformDrawingWidget(self.model.proxy_scene)
		self.addWidget(self.name_widget)
		self.addWidget(self.drawing_widget)
		self.ConnectSignals()

	def CreateWaveformNameValueWidget(self, model) -> QtWidgets.QTableView:
		name_value_widget = QtWidgets.QTableView(
			model = model,
			minimumWidth = 50
		)
		name_value_widget.verticalHeader().hide()
		name_value_widget.horizontalHeader().setStretchLastSection(True)
		name_value_widget.horizontalHeader().setFixedHeight(self.setting.Display.timeaxis_height)
		name_value_widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
		name_value_widget.verticalHeader().setMinimumSectionSize(0)
		name_value_widget.verticalHeader().setMaximumSectionSize(self.setting.Display.wave_stride)
		name_value_widget.verticalHeader().setDefaultSectionSize(self.setting.Display.wave_stride)
		return name_value_widget

	def CreateWaveformDrawingWidget(self, scene) -> WaveformDrawingWidget:
		drawing_widget = WaveformDrawingWidget(minimumWidth = 50)
		drawing_widget.setScene(scene)
		return drawing_widget

	def ConnectSignals(self):
		self.model.update_height_signal.connect(self.update_height_signal_callback)
		self.model.update_width_signal.connect(
			lambda w: self.drawing_widget.scale(self.setting.Display.initial_wave_width/w, 1)
		)
		self.drawing_widget.update_screenspce_timepoints_signal.connect(
			self.model.SetScreenspaceTimepoints
		)
		# Lock the scrollbar
		# self.drawing_widget.verticalScrollBar().valueChanged.connect(
		# 	lambda v: self.name_widget.verticalScrollBar().setValue(
		# 		(v - self.setting.Display.timeaxis_height) / self.setting.Display.wave_stride
		# 	)
		# )
		# self.name_widget.verticalScrollBar().valueChanged.connect(
		# 	lambda v: self.drawing_widget.verticalScrollBar().setValue(
		# 		v * self.setting.Display.wave_stride + self.setting.Display.timeaxis_height
		# 	)
		# )
		self.drawing_widget.verticalScrollBar().valueChanged.connect(lambda v: print(f"right {v}"))
		self.name_widget.verticalScrollBar().valueChanged.connect(lambda v: print(f"left {v}"))

	def update_height_signal_callback(self, h):
		old_w = self.drawing_widget.sceneRect().width()
		self.drawing_widget.setSceneRect(0, 0, old_w, h)
