from PySide6 import QtCore, QtGui, QtWidgets
from waveform import waveformloader
import numpy as np

HEADER_ = 50
HEIGHT_ = 20
PREHEIGHT_ = 5
POSTHEIGHT_ = 5
STRIDE_ = HEIGHT_ + PREHEIGHT_ + POSTHEIGHT_
INIT_WAVEFORM_WIDTH_ = 2000

# TODO shall be tree model
class WaveformProxyListModel(QtCore.QAbstractTableModel):
	def __init__(self):
		QtCore.QAbstractTableModel.__init__(self)
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

	def insertSignal(self, name, value):
		n = len(self.name_value_list)
		dummy = QtCore.QModelIndex()
		self.beginInsertRows(dummy, n, n)
		self.name_value_list.append((name, value))
		self.endInsertRows()

class WaveformModel(object):
	def __init__(self):
		self.timepoints_screenspace = None
		self.proxy_scene = QtWidgets.QGraphicsScene()
		# TODO shall be tree model
		self.proxy_list_model = WaveformProxyListModel()

class WaveformGraphicsView(QtWidgets.QGraphicsView):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setOptimizationFlags(QtWidgets.QGraphicsView.DontSavePainterState)
		# FullViewportUpdate since we do the crop by ourselves
		self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
		self.timepoints = None

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
		self.timepoints = (np.linspace(xmin, xmax, xtick, False, dtype=np.float64) + 0.5).astype('u8')
		QtWidgets.QGraphicsView.paintEvent(self, event)

class WaveformGraphicsItem(QtWidgets.QGraphicsItem):
	def __init__(self, model, signal_data):
		super().__init__()
		self.model = model
		self.signal_data = signal_data

	def boundingRect(self):
		return QtCore.QRect(0, 0, self.model.max_timepoint, HEIGHT_)

	def paint(self, painter, option, parent):
		graphics_view = parent.parent()
		# TODO is this always true?
		assert isinstance(graphics_view, WaveformGraphicsView)
		if graphics_view.timepoints is None:
			return
		painter.save()
		# color scheme
		green_pen = QtGui.QPen(QtCore.Qt.green)
		painter.setPen(green_pen)
		# disable all X transform, we compute on the screen space X values directly
		t = painter.transform()
		t.setMatrix(
			    1.0, t.m12(), t.m13(),
			t.m21(), t.m22(), t.m23(),
			    0.0, t.m32(), t.m33(),
		)
		painter.setTransform(t)
		# paint at screen space
		width = np.searchsorted(graphics_view.timepoints, self.model.max_timepoint)
		painter.drawLine(0, 0, width, 0)
		painter.drawLine(0, HEIGHT_, width, HEIGHT_)
		idx, tps, data01, dataxz = self.signal_data.GetValuesFromTimepoints(graphics_view.timepoints)
		for i in range(idx.size):
			painter.drawLine(idx[i], 0, idx[i], HEIGHT_)
		painter.restore()

class WaveformWidget(QtWidgets.QSplitter):
	def __init__(self):
		super().__init__(QtCore.Qt.Orientation.Horizontal, childrenCollapsible=False)
		self.model = WaveformModel()
		self.name_widget = QtWidgets.QTableView(
			model = self.model.proxy_list_model,
			minimumWidth = 50
		)
		self.name_widget.verticalHeader().hide()
		self.name_widget.horizontalHeader().setStretchLastSection(True)
		self.name_widget.horizontalHeader().setFixedHeight(HEADER_)
		self.name_widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
		self.name_widget.verticalHeader().setMinimumSectionSize(0)
		self.name_widget.verticalHeader().setMaximumSectionSize(STRIDE_)
		self.name_widget.verticalHeader().setDefaultSectionSize(STRIDE_)
		self.drawing_widget = WaveformGraphicsView(
			self.model.proxy_scene,
			minimumWidth = 50
		)
		self.drawing_widget.setBackgroundBrush(QtCore.Qt.black)
		self.drawing_widget.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		self.addWidget(self.name_widget)
		self.addWidget(self.drawing_widget)
		self.drawing_widget.verticalScrollBar().valueChanged.connect(lambda v: self.name_widget.verticalScrollBar().setValue(v/STRIDE_))
		self.name_widget.verticalScrollBar().valueChanged.connect(lambda v: self.drawing_widget.verticalScrollBar().setValue(v*STRIDE_))

	def setMaxTime(self, max_timepoint):
		self.model.max_timepoint = max_timepoint
		self.drawing_widget.scale(INIT_WAVEFORM_WIDTH_/max_timepoint, 1)
		self.drawing_widget.setSceneRect(0, 0, max_timepoint, 0)

	def addSignal(self, name, signal):
		witem = WaveformGraphicsItem(self.model, signal)
		witem.setPos(0, len(self.model.proxy_list_model.name_value_list)*STRIDE_+PREHEIGHT_+HEADER_)
		self.model.proxy_scene.addItem(witem)
		self.model.proxy_list_model.insertSignal(name, "XXX")
		self.drawing_widget.setSceneRect(0, 0, self.model.max_timepoint, len(self.model.proxy_list_model.name_value_list)*STRIDE_+HEADER_)