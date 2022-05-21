from PySide6 import QtCore, QtGui, QtWidgets
from Setting import GetSetting
import numpy as np

class WaveGraphicsItem(QtWidgets.QGraphicsItem):
	def __init__(self, model, wave_data):
		super().__init__()
		self.model = model # refer to model for common variables across the waveform
		self.wave_data = wave_data

	def boundingRect(self):
		return QtCore.QRect(0, 0, self.model.max_timepoint, self.model.setting.Display.wave_height)

	def paint(self, painter, option, parent):
		timepoints = self.model.screenspace_timepoints
		assert not timepoints is None
		wave_height = self.model.setting.Display.wave_height
		painter.save()
		# color scheme
		green_pen = QtGui.QPen(QtCore.Qt.green)
		painter.setPen(green_pen)
		# disable all X transform, we compute on the screen space X values directly
		t = painter.transform()
		t.setMatrix(
			    1.0, t.m12(), t.m13(),
			t.m21(), t.m22(), t.m23(),
			    0.0, t.m32(), t.m33(),
		)
		painter.setTransform(t)
		# paint at screen space
		# do not draw exceed this pixel
		max_width = np.searchsorted(timepoints, self.model.max_timepoint)
		painter.drawLine(0, 0, max_width, 0)
		painter.drawLine(0, wave_height, max_width, wave_height)
		idx, tps, data01, dataxz = self.wave_data.GetValuesFromTimepoints(timepoints)
		for i in range(idx.size):
			painter.drawLine(idx[i], 0, idx[i], wave_height)
		painter.restore()

# TODO shall be tree model
class WaveformProxyListModel(QtCore.QAbstractTableModel):
	def __init__(self):
		super().__init__()
		self.name_value_list = list()

	def rowCount(self, node_index):
		return len(self.name_value_list)

	def columnCount(self, node_index):
		return 2

	def data(self, node_index, role):
		return (
			self.name_value_list[node_index.row()][node_index.column()]
			if role == QtCore.Qt.DisplayRole
			else None
		)

	def headerData(self, section, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return "Value" if section == 1 else "Name"
		return None

	def InsertSignal(self, name, value):
		n = len(self.name_value_list)
		dummy = QtCore.QModelIndex()
		self.beginInsertRows(dummy, n, n)
		self.name_value_list.append((name, value))
		self.endInsertRows()

class WaveformModel(QtCore.QObject):
	update_width_signal = QtCore.Signal(int)
	update_height_signal = QtCore.Signal(int)
	def __init__(self):
		super().__init__()
		self.setting = GetSetting()
		self.max_timepoint = 1
		self.screenspace_timepoints = None
		self.screenspace_cursor_time = 0
		self.cursor_time = 0
		self.proxy_scene = QtWidgets.QGraphicsScene()
		# TODO shall be tree model
		self.proxy_list_model = WaveformProxyListModel()

	def SetScreenspaceTimepoints(self, timepoints):
		self.screenspace_timepoints = timepoints

	def SetScreenspaceCursorTime(self, t):
		pass

	def SetMaxTimepoint(self, max_timepoint):
		self.max_timepoint = max_timepoint
		self.update_width_signal.emit(max_timepoint)
		self.SetScreenspaceCursorTime(0)

	def AddWave(self, name, wave):
		witem = WaveGraphicsItem(self, wave)
		ypos = (
			self.NumSignal() * self.setting.Display.wave_stride +
			self.setting.Display.timeaxis_height + self.setting.Display.wave_spacing // 2
		)
		witem.setPos(0, ypos)
		self.proxy_scene.addItem(witem)
		self.proxy_list_model.InsertSignal(name, "XXX")
		self.update_height_signal.emit(ypos + self.setting.Display.wave_stride)

	def NumSignal(self):
		return len(self.proxy_list_model.name_value_list)