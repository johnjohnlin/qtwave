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
	PaintingAreaInfo,
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
	painting_area_info : PaintingAreaInfo
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
		self.painting_area_info = PaintingAreaInfo()
		self.ruler = RulerGraphicsItem(40)
		self.signals = list()

		self.ResetMaxTimestamp(100000)
		self.InitTestScene_()

	def ResetMaxTimestamp(self, max_timestamp):
		self.painting_area_info.max_timestamp = max_timestamp
		hsb = self.horizontalScrollBar()
		hsb.setMinimum(0)
		self.UpdateHorizontalPageStep(max_timestamp)

	def UpdateHorizontalPageStep(self, page_step : int):
		hsb = self.horizontalScrollBar()
		# Use 3/4 to allow scrolling a bit "righter" than max_timestamp
		hsb.setMaximum(self.painting_area_info.max_timestamp - page_step*3//4)
		hsb.setPageStep(page_step)

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
			item.sig.value01 = np.zeros_like(item.sig.timestamps, dtype=np.bool_)
			item.sig.value01[inversion::2] = 1
			self.signals.append(item)

	def _wheelEvent_HorizontalMove(self, delta : int) -> None:
		hsb = self.horizontalScrollBar()
		step = hsb.pageStep()//5
		translate = step if delta < 0 else -step
		hsb.setValue(min(hsb.maximum(), max(0, hsb.value() + translate)))

	def _wheelEvent_VerticalMove(self, delta : int) -> None:
		translate = 30 if delta < 0 else -30
		vsb = self.verticalScrollBar()
		vsb.setValue(vsb.value() + translate)

	def _wheelEvent_HorizontalScale(self, delta : int) -> None:
		hsb = self.horizontalScrollBar()
		scale = 1.25 if delta < 0 else 0.8
		self.UpdateHorizontalPageStep(max(30, min(int(hsb.pageStep()*scale), self.painting_area_info.max_timestamp)))

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

	def _UpdatePaintingAreaInfo(self) -> None:
		width = self.viewport.width()
		hsb = self.horizontalScrollBar()
		start_time = float(hsb.value())
		total_time_span = hsb.pageStep()
		self.painting_area_info.step_size = total_time_span / width
		self.painting_area_info.screenspace_timestamps = (np.linspace(
			start_time, start_time+total_time_span, width+1
		) + 0.5).astype(np.uint64) # 0.5 for rounding
		self.painting_area_info.dumpoff_pixels = np.zeros((width,), np.bool_,)

	def _PaintBackground(self, painter : QPainter) -> None:
		painter.fillRect(self.viewport.rect(), QColor("black"))

	def _PaintWave(self, painter : QPainter) -> None:
		saved_transform = painter.transform()
		vsb = self.verticalScrollBar()
		y_begin = vsb.value()
		y_end = y_begin + vsb.pageStep()
		painter.translate(0, 40-y_begin%35)
		for sig in self.signals[(y_begin//35):((y_end+69)//35)]:
			sig.PaintByTimestamp(painter, self.painting_area_info)
			painter.translate(0, 35)
		painter.setTransform(saved_transform)

	def _PaintTimeAxis(self, painter : QPainter) -> None:
		self.ruler.PaintByTimestamp(painter, self.painting_area_info)

	def paintEvent(self, event):
		painter = QPainter(self.viewport)
		self._UpdatePaintingAreaInfo()
		self._PaintBackground(painter)
		self._PaintWave(painter)
		self._PaintTimeAxis(painter)
		painter.end()

	def resizeEvent(self, event):
		self.verticalScrollBar().setPageStep(event.size().height())
		super().resizeEvent(event)
