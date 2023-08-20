from PySide6 import QtCore, QtGui, QtWidgets
from WaveformModel import WaveformModel
from Setting import GetSetting
import numpy as np

class WaveformDrawingWidget(QtWidgets.QGraphicsView):
	update_view_geometry = QtCore.Signal(float, float, int)
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setOptimizationFlags(QtWidgets.QGraphicsView.DontSavePainterState)
		# FullViewportUpdate since we do the crop by ourselves
		self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
		self.setBackgroundBrush(QtCore.Qt.black)
		self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		self.setting = GetSetting()

	def wheelEvent(self, event):
		delta = event.pixelDelta().y()
		if event.modifiers() == QtCore.Qt.ControlModifier:
			zoom_xfactor = 3/2 if delta > 0 else 2/3
			self.scale(zoom_xfactor, 1.0)
		elif event.modifiers() == QtCore.Qt.ShiftModifier:
			if self.setting.Display.horizontal_scroll_flip:
				delta = -delta
			self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta)
		else:
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta)

	def paintEvent(self, event):
		pixel_step = float(1.0 / self.transform().m11())
		pixel0_ofs = float(self.horizontalScrollBar().value()) * pixel_step
		width = int(self.size().width())
		self.update_view_geometry.emit(
			pixel0_ofs, pixel_step, width
		)
		QtWidgets.QGraphicsView.paintEvent(self, event)
