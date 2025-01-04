import math
import numpy as np
import numpy.typing as npt
from PyQt6.QtGui import (
	QColorConstants,
	QPainter,
	QPainterPath,
	QPen,
	QTransform,
)
from PyQt6.QtCore import (
	QRectF,
)

class AbstractTimestampSampledGraphicsItem:
	height : int

	def __init__(self, height : int):
		self.height = height

	def PaintByTimestamp(
		self,
		# with this painter, you shall paint in x=[0, SST.size-1), y=[0,self.height]
		painter : QPainter,
		# SST: 1D array
		screenspace_timestamps : npt.NDArray[np.uint64],
		# (SST[-1]-SST[0]) / (SST.size-1)
		step_size : float
	):
		raise NotImplementedError()

class RulerGraphicsItem(AbstractTimestampSampledGraphicsItem):
	def __init__(self, height : int):
		super().__init__(height)

	def PaintByTimestamp(
		self,
		painter : QPainter,
		screenspace_timestamps : npt.NDArray[np.uint64],
		step_size : float
	):
		# Setup GUI pen
		painter.fillRect(0, 0, screenspace_timestamps.size, self.height, QColorConstants.DarkGray)

		# each scale is spaced by 10**some_int
		# The distance between two scale > kMinScaleDistance pixels
		kMinScaleDistance = 30
		scale_lowerbound = kMinScaleDistance * step_size
		scale = pow(10, math.ceil(math.log(scale_lowerbound, 10)))

		# Setup GUI pen
		painter.setPen(QPen(QColorConstants.Red))

		# TODO: too many division, binary search shall be better
		for i in range(1, screenspace_timestamps.size):
			if screenspace_timestamps[i]//scale != screenspace_timestamps[i-1]//scale:
				painter.drawLine(i, 0, i, self.height)

class OneBitSignal:
	timestamps : npt.NDArray[np.uint64]
	value01 : npt.NDArray[np.bool_]
	def __init__(self):
		pass

class OneBitGraphicsItem(AbstractTimestampSampledGraphicsItem):
	sig : OneBitSignal
	def __init__(self, height : int, sig : OneBitSignal):
		super().__init__(height)
		self.sig = sig

	def PaintByTimestamp(
		self,
		painter : QPainter,
		screenspace_timestamps : npt.NDArray[np.uint64],
		step_size : float
	):
		# Setup GUI pen
		pen = QPen(QColorConstants.Green)
		painter.setPen(pen)
		idx_in_waveform = np.searchsorted(self.sig.timestamps, screenspace_timestamps)
		segment_begin = 0
		width = screenspace_timestamps.size-1
		for i in range(width):
			if idx_in_waveform[i] == idx_in_waveform[i+1]:
				continue
			painter.drawLine(i, 0, i, self.height)
			if segment_begin < (i-1):
				y = 0 if bool(self.sig.value01[idx_in_waveform[segment_begin]]) else self.height
				painter.drawLine(segment_begin, y, i, y)
			segment_begin = i
