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
		# with this painter, you shall paint in x=[0, SST.size), y=[0,self.height]
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
		# each scale is spaced by 10**some_int
		# The distance between two scale > kMinScaleDistance pixels
		kMinScaleDistance = 30
		scale_lowerbound = kMinScaleDistance * step_size
		scale = pow(10, math.ceil(math.log(scale_lowerbound, 10)))

		# Setup GUI pen
		pen = QPen(QColorConstants.Red)
		pen.setCosmetic(True)
		painter.setPen(pen)

		# TODO: too many division, binary search shall be better
		for i in range(1, screenspace_timestamps.size):
			if screenspace_timestamps[i]//scale != screenspace_timestamps[i-1]//scale:
				painter.drawLine(i, 0, i, self.height)
