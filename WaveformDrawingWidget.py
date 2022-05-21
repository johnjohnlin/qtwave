from PySide6 import QtCore, QtGui, QtWidgets
from Setting import GetSetting
from WaveformModel import WaveformModel
import numpy as np

class WaveformDrawingWidget(QtWidgets.QGraphicsView):
	update_screenspce_timepoints_signal = QtCore.Signal(object)
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setOptimizationFlags(QtWidgets.QGraphicsView.DontSavePainterState)
		# FullViewportUpdate since we do the crop by ourselves
		self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
		self.setBackgroundBrush(QtCore.Qt.black)
		self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

	def wheelEvent(self, event):
		delta = event.pixelDelta().y()
		if event.modifiers() == QtCore.Qt.ControlModifier:
			zoom_xfactor = 3/2 if delta > 0 else 2/3
			self.scale(zoom_xfactor, 1.0)
		elif event.modifiers() == QtCore.Qt.ShiftModifier:
			self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta)
		else:
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta)

	def paintEvent(self, event):
		sz = self.size()
		waveform_rect = self.mapToScene(QtCore.QRect(QtCore.QPoint(0, 0), sz))
		xtick = sz.width()
		xmin = waveform_rect[0].x()
		xmax = waveform_rect[1].x()
		self.update_screenspce_timepoints_signal.emit(
			(np.linspace(xmin, xmax, xtick, False, dtype=np.float64) + 0.5).astype('u8')
		)
		QtWidgets.QGraphicsView.paintEvent(self, event)