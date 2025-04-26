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
from dataclasses import dataclass
from enum import Enum

@dataclass
class PaintingAreaInfo:
	"""
	Store the WaveformWidget's screenspace timestamp information based on its width, zooming and position.
	WaveformWidget uses them to calculate the timestamp span value of each pixel on the monitor.
	If a pixel spans timestamp=[1000,1300), then for 1-bit signal, you shall draw a vertical bar at this pixel

	Illustration when painting_width=4, step_size=300.0:
	1000  1300  1600  1900  2200       screenspace_timestamps
	|---->|---->|---->|---->|
	  px0   px1   px1   px3            screen pixel

	Attributes:
		painting_width:
			The area you can paint, > 0
		step_size:
			See below
		screenspace_timestamps:
			A 1D array with shape=(painting_width+1,); arithmetic sequence with difference = step_size.
			Rounded to uint64_t.
			This represents the spans of all pixels in the screen, back-to-back.
		max_timestamp:
			The max timestamp of the waveform
	"""
	step_size : float = math.nan
	screenspace_timestamps : npt.NDArray[np.uint64] = None
	max_timestamp : int = 1

	@property
	def painting_width(self) -> int:
		return self.screenspace_timestamps.size-1

class AbstractTimestampSampledGraphicsItem:
	"""
	Represent a rectanglur items to be drawn on the WaveformWidget
	"""
	height : int

	def __init__(self, height : int):
		self.height = height

	def PaintByTimestamp(
		self,
		painter : QPainter,
		pinfo: PaintingAreaInfo
	):
		raise NotImplementedError()

class RulerGraphicsItem(AbstractTimestampSampledGraphicsItem):
	def __init__(self, height : int):
		super().__init__(height)

	def PaintByTimestamp(
		self,
		painter : QPainter,
		pinfo: PaintingAreaInfo
	):
		painter.fillRect(0, 0, pinfo.painting_width, self.height, QColorConstants.DarkGray)

		# each scale is spaced by 10**some_int
		# The distance between two scale > kMinScaleDistance pixels
		kMinScaleDistance = 30
		scale_lowerbound = kMinScaleDistance * pinfo.step_size
		scale = pow(10, math.ceil(math.log(scale_lowerbound, 10)))

		# Setup GUI pen
		painter.setPen(QPen(QColorConstants.Red))

		def MustTick() -> npt.NDArray[np.uint32]:
			tick = np.zeros(pinfo.painting_width, np.uint64)
			ts = pinfo.screenspace_timestamps.copy()
			ts //= np.uint64(scale)
			tick += ts[1:] != ts[:-1]
			ts //= 10
			tick += ts[1:] != ts[:-1]
			# return tick 0 : no tick, 1 : small tick, 2 : large tick
			return tick
		tick = MustTick()
		for i, t in enumerate(tick):
			if tick[i] != 0:
				painter.drawLine(i, 0, i, self.height*tick[i]//2)

class FourValue(Enum):
	e0 = 0
	e1 = 1
	eX = 2
	eZ = 3

	@staticmethod
	def FromBools(e01 : bool, is_xz : bool):
		return (
			(FourValue.eZ if e01 else FourValue.eX)
			if is_xz
			else (FourValue.e1 if e01 else FourValue.e0)
		)

@dataclass
class OneBitSignal:
	timestamps : npt.NDArray[np.uint64] = None
	value01 : npt.NDArray[np.bool_] = None
	valuexz : npt.NDArray[np.bool_] = None

	def GetFourValue(self, idx: int):
		return FourValue.FromBools(
			self.value01[idx],
			False if self.valuexz is None else self.valuexz[idx],
		)


class OneBitGraphicsItem(AbstractTimestampSampledGraphicsItem):
	sig : OneBitSignal
	painter : QPainter

	def __init__(self, height : int, sig : OneBitSignal):
		super().__init__(height)
		self.sig = sig

	def PaintValueHold(self, left: int, right: int, value: FourValue):
		y = 0 if value == FourValue.e1 else self.height
		self.painter.drawLine(left, y, right, y)

	def PaintValueChange(self, x_position: int):
		self.painter.drawLine(x_position, 0, x_position, self.height)

	def PaintByTimestamp(
		self,
		painter : QPainter,
		pinfo: PaintingAreaInfo
	):
		# Setup GUI pen
		pen = QPen(QColorConstants.Green)
		self.painter = painter
		painter.setPen(pen)
		idx_in_waveform = np.searchsorted(self.sig.timestamps, pinfo.screenspace_timestamps)
		segment_begin = 0
		prev_value = FourValue.eX if idx_in_waveform[0] == 0 else self.sig.GetFourValue(idx_in_waveform[0]-1)
		width = pinfo.painting_width
		for i in range(width):
			has_value_change = idx_in_waveform[i] != idx_in_waveform[i+1]
			end_of_wave = i == width-1 or pinfo.screenspace_timestamps[i+1] > pinfo.max_timestamp
			if has_value_change or end_of_wave:
				if segment_begin < (i-1):
					self.PaintValueHold(segment_begin, i, prev_value)
			if has_value_change:
				self.PaintValueChange(i)
				segment_begin = i
				prev_value = self.sig.GetFourValue(idx_in_waveform[i+1]-1)
			if end_of_wave:
				break
