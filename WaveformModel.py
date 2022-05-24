from cgitb import text
from os import sched_get_priority_max
from typing import *
import wave
from PySide6 import QtCore, QtGui, QtWidgets
from Setting import GetSetting
import numpy as np
from enum import Enum, auto
from waveform.waveformloader import SignalData

def LocatePixelsIncludingValueChange(
	value_changing_timepoints,
	screenspace_timepoints,
	screenspace_pixels
):
	i = np.searchsorted(value_changing_timepoints, screenspace_timepoints, side='left')
	nonzero_timepoints_bool = np.diff(i) != 0
	if i[0] != 0:
		nonzero_timepoints_bool[0] = True
	return (
		screenspace_timepoints[:-1][nonzero_timepoints_bool].copy(),
		screenspace_pixels[:-1][nonzero_timepoints_bool].copy(),
		(i[1:][nonzero_timepoints_bool]-1).copy()
	)

class TimeAxisGraphicsItem(QtWidgets.QGraphicsItem):
	def __init__(self, model):
		super().__init__()
		self.model = model # refer to model for common variables across the waveform

	def boundingRect(self):
		return QtCore.QRect(0, 0, self.model.SceneWidth(), self.model.SceneHeight())

	def paint(self, painter, option, parent):
		maximal_zoom = self.model.setting.Display.maximal_zoom
		pixels = self.model.screenspace_pixels
		timepoints = self.model.screenspace_timepoints
		if timepoints is None or timepoints.size < 2:
			return
		time_diff = timepoints[-1] - timepoints[0]
		screenspace_time_diff = pixels[-1] - pixels[0]
		# compute the time
		timescale = 1
		# timescale / (time_diff / screenspace_time_diff) > maximal_zoom
		while (
			screenspace_time_diff * timescale <
			maximal_zoom * time_diff
		):
			timescale *= 10
		painter.save()
		painter.resetTransform()
		hline_float = self.model.setting.Display.timeaxis_float
		timeaxis_height = self.model.setting.Display.timeaxis_height
		hline_ypos = timeaxis_height - hline_float
		# Draw hline
		painter.setPen(QtCore.Qt.blue)
		painter.drawLine(pixels[0], hline_ypos, pixels[-1], hline_ypos)
		# Draw ticks
		integer_timepoints = np.arange(
			timepoints[:1] // timescale,
			timepoints[-1:] // timescale + 1,
			dtype = 'u8'
		) * timescale
		for i, pixel_idx in enumerate(np.searchsorted(timepoints, integer_timepoints, side='right')):
			if pixel_idx == 0:
				continue
			x = pixels[pixel_idx-1]
			if integer_timepoints[i] % (10*timescale) == 0:
				# coarse ticks
				painter.setPen(QtCore.Qt.white)
				painter.drawText(
					x-6*maximal_zoom, 0, 12*maximal_zoom, hline_ypos,
					QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter, str(integer_timepoints[i])
				)
				painter.setPen(QtCore.Qt.blue)
				painter.drawLine(x, hline_ypos, x, parent.parent().height())
			else:
				# fine ticks
				painter.setPen(QtCore.Qt.blue)
				painter.drawLine(x, hline_ypos, x, timeaxis_height)
		# draw coarse tick
		painter.restore()

class SignalDrawType(Enum):
	ONE_BIT_0 = auto()
	ONE_BIT_1 = auto()
	ONE_BIT_X = auto()
	ONE_BIT_Z = auto()
	MULTI_BIT_0 = auto()
	MULTI_BIT_1 = auto()
	MULTI_BIT_2 = auto()
	MULTI_BIT_X = auto()
	MULTI_BIT_Z = auto()

class DrawSegment:
	right_open: bool
	signal_draw_type: SignalDrawType
	text: str
	left: int
	right: int

	def __init__(self):
		self.right_open = False
		self.signal_draw_type = SignalDrawType.ONE_BIT_0
		self.text = str()
		self.left = 0
		self.right = 0

class WaveGraphicsItem(QtWidgets.QGraphicsItem):
	wave_data: SignalData
	model: 'WaveformModel'

	def __init__(self, model, wave_data):
		super().__init__()
		self.model = model # refer to model for common variables across the waveform
		self.wave_data = wave_data

	def boundingRect(self):
		return QtCore.QRect(0, 0, self.model.max_timepoint, self.model.setting.Display.wave_height)

	def paint(self, painter, option, parent):
		if self.pos().y() < 0:
			return
		(
			changing_screenspace_timepoints,
			changing_screenspace_pixels,
			indices_in_wave,
		) = LocatePixelsIncludingValueChange(
			self.wave_data.timepoints_,
			self.model.screenspace_timepoints,
			self.model.screenspace_pixels
		)
		draw_segments = list()
		for i in range(changing_screenspace_timepoints.size):
			is_last = i == changing_screenspace_timepoints.size-1
			left = changing_screenspace_pixels[i]
			right = (
				self.model.screenspace_pixels[-1]-1
				if is_last
				else changing_screenspace_pixels[i+1]
			)
			if left >= right:
				continue
			seg = DrawSegment()
			seg.right_open = is_last
			seg.left = left
			seg.right = right
			value_idx = indices_in_wave[i]
			tp, data01, dataxz = self.wave_data[value_idx]
			if self.wave_data.nbit_ == 1:
				data01 = bool(data01)
				dataxz = bool(dataxz)
				if dataxz:
					if data01:
						seg.signal_draw_type = SignalDrawType.ONE_BIT_Z
						seg.text = "z"
					else:
						seg.signal_draw_type = SignalDrawType.ONE_BIT_X
						seg.text = "x"
				else:
					if data01:
						seg.signal_draw_type = SignalDrawType.ONE_BIT_1
						seg.text = "1"
					else:
						seg.signal_draw_type = SignalDrawType.ONE_BIT_0
						seg.text = "0"
			else:
				seg.signal_draw_type = SignalDrawType.MULTI_BIT_2
				seg.text = str(data01)
			draw_segments.append(seg)
		self._RenderSegments(painter, draw_segments)

	def _SetTransformToScreenspace(self, painter: QtGui.QPainter):
		painter.save()
		t = painter.transform()
		t.setMatrix(
			    1.0, t.m12(), t.m13(),
			t.m21(), t.m22(), t.m23(),
			    0.0, t.m32(), t.m33(),
		)
		painter.setTransform(t)

	def _ResetTransform(self, painter: QtGui.QPainter):
		painter.restore()

	def _RenderSegments(self, painter: QtGui.QPainter, draw_segments: List[DrawSegment]):
		wave_height = self.model.setting.Display.wave_height
		transit = self.model.setting.Display.wave_transit
		display_text_threshold = self.model.setting.Display.display_text_threshold
		text_margin = self.model.setting.Display.text_margin
		self._SetTransformToScreenspace(painter)
		painter.setPen(QtCore.Qt.green)
		for segment in draw_segments:
			left = segment.left
			right = segment.right
			stype = segment.signal_draw_type
			if (
				stype == SignalDrawType.ONE_BIT_0 or
				stype == SignalDrawType.ONE_BIT_1 or
				stype == SignalDrawType.ONE_BIT_X or
				stype == SignalDrawType.ONE_BIT_Z
			):
				wave_height_half = (wave_height + 1) // 2
				painter.drawLine(left, 0, left, wave_height)
				if right > left+1:
					if stype == SignalDrawType.ONE_BIT_0:
						painter.drawLine(left, wave_height, right, wave_height)
					if stype == SignalDrawType.ONE_BIT_1:
						painter.drawLine(left, 0, right, 0)
					if stype == SignalDrawType.ONE_BIT_X:
						painter.drawLine(left, wave_height, right, wave_height)
						painter.drawLine(left, 0, right, 0)
					if stype == SignalDrawType.ONE_BIT_Z:
						painter.drawLine(left, wave_height_half, right, wave_height_half)
			else:
				wave_height_half = wave_height * 0.5
				left1 = left + .5
				left2 = left1 + transit
				painter.drawLine(QtCore.QPointF(left1, wave_height_half), QtCore.QPointF(left2, 0          ))
				painter.drawLine(QtCore.QPointF(left1, wave_height_half), QtCore.QPointF(left2, wave_height))
				left += transit
				if not segment.right_open:
					right2 = right + .5
					right1 = right2 - transit
					painter.drawLine(QtCore.QPointF(right1, 0          ), QtCore.QPointF(right2, wave_height_half))
					painter.drawLine(QtCore.QPointF(right1, wave_height), QtCore.QPointF(right2, wave_height_half))
					right -= transit
				if right > left+1:
					painter.drawLine(left, 0, right, 0)
					painter.drawLine(left, wave_height, right, wave_height)
				left += text_margin
				right -= text_margin
				left = max(left, 0)
				if right-left > display_text_threshold:
					painter.drawText(
						left, 0, right-left, wave_height,
						QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
						segment.text
					)
		self._ResetTransform(painter)

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
		self.proxy_scene.addItem(TimeAxisGraphicsItem(self))
		# TODO shall be tree model
		self.proxy_list_model = WaveformProxyListModel()

	def SetScreenspaceTimepoints(self, pixel0_ofs: float, pixel_step: float, width: int):
		expand = self.setting.Display.wave_transit * 2
		# sample screenspace pixels
		screenspace_pixels = np.arange(-expand, width+expand+1, dtype=np.int32)
		screenspace_timepoints = screenspace_pixels.astype(np.float64) * pixel_step + pixel0_ofs
		valid_beg = np.searchsorted(screenspace_timepoints, np.float64(0), side='left')
		valid_end = np.searchsorted(screenspace_timepoints, np.float64(self.max_timepoint), side='left')
		cross_max_timepoint = valid_end != screenspace_pixels.size
		if cross_max_timepoint:
			valid_end += 1
		self.screenspace_pixels = screenspace_pixels[valid_beg:valid_end].copy()
		self.screenspace_timepoints = screenspace_timepoints[valid_beg:valid_end].astype('u8')
		if cross_max_timepoint:
			self.screenspace_timepoints[-1] = self.max_timepoint

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

	def SceneWidth(self):
		return self.max_timepoint

	def SceneHeight(self):
		return self.NumSignal() * self.setting.Display.wave_stride + self.setting.Display.timeaxis_height
