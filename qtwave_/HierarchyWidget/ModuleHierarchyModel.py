from PyQt6.QtCore import (
	QAbstractItemModel,
	QModelIndex,
	Qt,
)
from qtwave_.Waveform import HierarchyTreeNode
from typing import *

class ModuleHierarchyModel(QAbstractItemModel):
	root : Optional[HierarchyTreeNode]

	def QModelIndexToNode(self, i : QModelIndex) -> HierarchyTreeNode:
		n : HierarchyTreeNode = i.internalPointer() if i.isValid() else self.root
		return n

	def columnCount(self, parent = QModelIndex()) -> int:
		return 1

	def rowCount(self, parent = QModelIndex()) -> int:
		l = len(self.QModelIndexToNode(parent).module_data.children)
		return l

	def index(self, row: int, column: int, parent = QModelIndex()) -> QModelIndex:
		children = self.QModelIndexToNode(parent).module_data.children
		if row < len(children) and column < 2:
			return QAbstractItemModel.createIndex(self, row, column, children[row])
		return QModelIndex()

	def parent(self, index : QModelIndex) -> QModelIndex:
		if index.isValid():
			parent : HierarchyTreeNode = index.internalPointer().parent
			if not parent is None:
				return QAbstractItemModel.createIndex(self, parent.nth_child, 0, parent)
		return QModelIndex()

	def headerData(self, x : int, orientation, role = Qt.ItemDataRole.DisplayRole):
		if (
			role != Qt.ItemDataRole.DisplayRole or
			orientation != Qt.Orientation.Horizontal
		):
			return None
		return ["Name"][x]

	def data(self, index: QModelIndex, role):
		if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
			node = index.internalPointer()
			x = index.column()
			if x == 0:
				return node.module_data.module_name
		return None

	def __init__(self):
		super().__init__()
		self.root = None

	def SetRoot(self, root : HierarchyTreeNode):
		self.root = root
