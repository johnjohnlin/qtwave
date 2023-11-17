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
)
import numpy as np
from typing import *
import math

class WaveformGraphWidget(QAbstractScrollArea):
	viewport : QWidget
	ruler : RulerGraphicsItem
	screenspace_step_size : float

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

#	def InitTestScene(self):
#		for i in range(4):
#			item = OneBitWaveGraphicsItem(1000, 100, i)
#			item.setPos(0, 110*i+100)
#			self.scene.addItem(item)

	def _UpdateScreenspaceTimestamp(self) -> None:
		width = self.viewport.width()
		# resize storage
		if self.screenspace_timestamps_storage.size < width:
			self.screenspace_timestamps_storage = np.empty((width,), dtype=np.uint64)
		# slicing from storage
		self.screenspace_timestamps = self.screenspace_timestamps_storage[:width]
		# count time sample
		hsb = self.horizontalScrollBar()
		start_time = hsb.value() + 0.5
		self.step_size = hsb.pageStep() / width
		for i in range(width):
			self.screenspace_timestamps[i] = int(start_time + self.step_size*i)

	def _PaintBackground(self, painter : QPainter) -> None:
		painter.fillRect(self.viewport.rect(), QColor("black"))

	def _PaintWave(self, painter : QPainter) -> None:
		pass

	def _PaintTimeAxis(self, painter : QPainter) -> None:
		self.ruler.PaintByTimestamp(painter, self.screenspace_timestamps, self.step_size)

	def paintEvent(self, event):
		painter = QPainter(self.viewport)
		self._UpdateScreenspaceTimestamp()
		self._PaintBackground(painter)
		self._PaintWave(painter)
		self._PaintTimeAxis(painter)
		painter.end()
