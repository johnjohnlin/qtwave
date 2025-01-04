# import math
from PyQt6.QtGui import (
	QColor,
	QPaintEvent,
	QPainter,
 	QPen,
 	QWheelEvent,
)
from PyQt6.QtWidgets import (
	QAbstractScrollArea,
)
from PyQt6.QtCore import (
	Qt,
)
from PyQt6.QtWidgets import (
	QScrollArea,
	QWidget,
)
from qtwave_.WaveformWidget.WaveGraphicsItem import (
	AbstractTimestampSampledGraphicsItem,
	RulerGraphicsItem,
	OneBitGraphicsItem,
	OneBitSignal,
)
import numpy as np
from typing import *
import math, itertools

class WaveformGraphWidget(QAbstractScrollArea):
	viewport : QWidget
	screenspace_step_size : float
	# graphic items
	ruler : RulerGraphicsItem
	signals : List[AbstractTimestampSampledGraphicsItem]

	def __init__(self):
		super().__init__()
		self.setMinimumSize(500, 300)
		self.viewport = QWidget()
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setViewport(self.viewport)
		vsb = self.verticalScrollBar()
		vsb.setPageStep(self.viewport.height())
		vsb.setMaximum(3000-self.viewport.height())
		hsb = self.horizontalScrollBar()
		hsb.setMinimum(0)
		hsb.setMaximum(0)
		hsb.setPageStep(100000)
		self.ruler = RulerGraphicsItem(40)

		self.screenspace_timestamps_storage = np.empty((1,), dtype=np.uint64)
		self.screenspace_timestamps = self.screenspace_timestamps_storage
		self.screenspace_step_size = math.nan
		self.signals = list()

		self.InitTestScene_()

	def InitTestScene_(self):
		kBasePeriod = 32
		kDuties = [1, 3, 9, 16]
		for multiplier_log5, duty, inversion in itertools.product(range(7), kDuties, range(2)):
			item = OneBitGraphicsItem(30, OneBitSignal())
			multiplier = (5**multiplier_log5)
			period = multiplier * kBasePeriod
			half_period = multiplier * duty
			item.sig.timestamps = np.repeat(np.arange(0, 100000, period), 2)
			item.sig.timestamps[1::2] += half_period
			item.sig.value01 = np.zeros((1000,), dtype=np.bool_)
			item.sig.value01[inversion::2] = 1
			self.signals.append(item)

	def _wheelEvent_HorizontalMove(self, delta : int) -> None:
		hsb = self.horizontalScrollBar()
		step = int(hsb.pageStep()*0.2)
		translate = step if delta < 0 else -step
		hsb.setValue(min(hsb.maximum(), max(0, hsb.value() + translate)))

	def _wheelEvent_VerticalMove(self, delta : int) -> None:
		translate = 30 if delta < 0 else -30
		vsb = self.verticalScrollBar()
		vsb.setValue(vsb.value() + translate)

	def _wheelEvent_HorizontalScale(self, delta : int) -> None:
		hsb = self.horizontalScrollBar()
		scale = 1.25 if delta < 0 else 0.8
		hsb.setPageStep(max(30, min(int(hsb.pageStep()*scale), 100000)))
		hsb.setMaximum(100000-hsb.pageStep())

	def wheelEvent(self, event: Optional[QWheelEvent]) -> None:
		modifier = event.modifiers()
		ctrl = modifier & Qt.KeyboardModifier.ControlModifier
		shift = modifier & Qt.KeyboardModifier.ShiftModifier
		dx = event.angleDelta().x()
		dy = event.angleDelta().y()
		delta_x1y0 = math.fabs(dx) > math.fabs(dy)
		delta = dx if delta_x1y0 else dy
		if delta_x1y0 or shift:
			self._wheelEvent_HorizontalMove(delta)
		elif ctrl:
			self._wheelEvent_HorizontalScale(delta)
		else:
			self._wheelEvent_VerticalMove(delta)
		event.accept()
		self.update()

	def _UpdateScreenspaceTimestamp(self) -> None:
		width = self.viewport.width()+1
		# resize storage
		if self.screenspace_timestamps_storage.size < width:
			self.screenspace_timestamps_storage = np.empty((width,), dtype=np.uint64)
		# slicing from storage
		self.screenspace_timestamps = self.screenspace_timestamps_storage[:width]
		# count time sample
		hsb = self.horizontalScrollBar()
		start_time = float(hsb.value())
		self.step_size = hsb.pageStep() / width
		for i in range(width):
			timestamp = int(start_time + self.step_size*i)
			self.screenspace_timestamps[i] = timestamp
			if timestamp > 100000:
				self.screenspace_timestamps = self.screenspace_timestamps[:i+1]
				break

	def _PaintBackground(self, painter : QPainter) -> None:
		painter.fillRect(self.viewport.rect(), QColor("black"))

	def _PaintWave(self, painter : QPainter) -> None:
		saved_transform = painter.transform()
		vsb = self.verticalScrollBar()
		y_begin = vsb.value()
		y_end = y_begin + vsb.pageStep()
		painter.translate(0, 40-y_begin%35)
		for sig in self.signals[(y_begin//35):((y_end+69)//35)]:
			sig.PaintByTimestamp(painter, self.screenspace_timestamps, self.step_size)
			painter.translate(0, 35)
		painter.setTransform(saved_transform)

	def _PaintTimeAxis(self, painter : QPainter) -> None:
		self.ruler.PaintByTimestamp(painter, self.screenspace_timestamps, self.step_size)

	def paintEvent(self, event):
		painter = QPainter(self.viewport)
		self._UpdateScreenspaceTimestamp()
		self._PaintBackground(painter)
		self._PaintWave(painter)
		self._PaintTimeAxis(painter)
		painter.end()
