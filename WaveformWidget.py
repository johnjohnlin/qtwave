from PySide6 import QtCore, QtGui, QtWidgets
from waveform import waveformloader
import numpy as np

class WaveformGraphicsView(QtWidgets.QGraphicsView):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

	def setTimepoints(self, timepoints):
		self.timepoints = timepoints

	def setSignalDdta(self, signal_data):
		self.signal_data = signal_data

	def resizeEvent(self, event):
		print(event.size())
		QtWidgets.QGraphicsView.resizeEvent(self, event)

	def wheelEvent(self, event):
		delta = event.pixelDelta().y()
		if event.modifiers() == QtCore.Qt.ControlModifier:
			zoom_xfactor = 3/2 if delta > 0 else 2/3
			self.scale(zoom_xfactor, 1.0)
		elif event.modifiers() == QtCore.Qt.ShiftModifier:
			self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta)
		else:
			self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta)

"""
class WaveformGraphicsItem(QtWidgets.QGraphicsItem):
	def boundingRect(self):
		pass

	def paint(self, event):
		pass
	"""

class WaveformWidget(QtWidgets.QSplitter):
	def __init__(self):
		super().__init__(QtCore.Qt.Orientation.Horizontal, childrenCollapsible=False)
		self.tmp_scene = QtWidgets.QGraphicsScene()
		self.name_widget = QtWidgets.QTreeView(
			headerHidden = False,
			minimumWidth = 50
		)
		self.drawing_widget = WaveformGraphicsView(
			self.tmp_scene,
			minimumWidth = 50
		)
		self.TmpModel()
		self.drawing_widget.setBackgroundBrush(QtCore.Qt.black)
		self.addWidget(self.name_widget)
		self.addWidget(self.drawing_widget)

	def TmpModel(self):
		wave = waveformloader.Waveform("waveform/test_ahb_example.fst")
		HEIGHT = 20
		HSTRIDE = 30
		XRANGE = 1000
		ofs = 0
		timepoints = np.arange(XRANGE)*1400
		green_pen = QtGui.QPen(QtCore.Qt.green)
		green_pen.setCosmetic(True)
		text_font = QtGui.QFont("monospace", pointSize=HEIGHT*0.6)
		for k, v in wave.signal_data_.items():
			idx, tps, data01, dataxz = v.GetValuesFromTimepoints(timepoints)
			self.tmp_scene.addLine(0, ofs, XRANGE, ofs, green_pen)
			self.tmp_scene.addLine(0, ofs+HEIGHT, XRANGE, ofs+HEIGHT, green_pen)
			for i in range(idx.size):
				self.tmp_scene.addLine(idx[i], ofs, idx[i], ofs+HEIGHT, green_pen)
				if i > 0 and idx[i] - idx[i-1] > 10:
					x = (idx[i]+idx[i-1])*0.5
					y = ofs-HEIGHT*0.5
					txt = self.tmp_scene.addText(f"{data01[i]}", text_font)
					txt.setPos(x, y)
					txt.setDefaultTextColor("white")
			ofs += HSTRIDE