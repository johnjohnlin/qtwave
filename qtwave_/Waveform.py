from typing import *
from enum import Enum
import numpy as np
import numpy.typing as npt
import logging
logger = logging.Logger(__file__)

class SpecialTimestampIndex(Enum):
	eTurnOff = np.int64(-1)
	eNoChange = np.int64(-2)

def SampleWaveformTimestampsIndexFromScreenspaceTimestamps(
	timestamps_wave : npt.NDArray[np.int64],
	timestamps_screenspace : npt.NDArray[np.int64]
):
	"""
		Input:
			timestamps_wave = (M), int64
			timestamps_screenspace = (N), int64
		Return:
			(N), int64
	"""
	idx = np.searchsorted(timestamps_wave, timestamps_screenspace, side='left')
	is_nochange = idx[1:] == idx[:-1]
	idx[1:][is_nochange] = SpecialTimestampIndex.eNoChange
	return idx

class SignalData:
	signal_name : str
	bit_width : int
	# TODO : Can we compress this?
	timestamps : None | npt.NDArray[np.uint64]
	# TODO
	# The size is timestampes.size*ceil(bit_width/64) (1D array),
	# However, we shall use shorter uint for small integers
	data : None | npt.NDArray[np.uint64]
	selected : bool
	is_created_from_file : bool

	def __init__(self, signal_name : str, bit_width : int):
		self.signal_name = signal_name
		self.bit_width = bit_width
		self.timestamps = None
		self.data = None
		self.selected = False
		self.is_created_from_file = False

	def SetTimestampsAndData(self, timestamps, data):
		self.timestamps = np.array(timestamps, np.uint64)
		self.data = np.array(data, np.uint64)
		if (
			len(self.timestamps.shape) != 1 or
			len(self.data.shape) != 1 or
			self.data.size != self.word_per_sample * self.num_sample
		):
			logger.critical(f"Invalid array size {self.timestamps.shape} and {self.data.shape}")
		return (self.bit_width + 63) // 64

	@property
	def word_per_sample(self):
		return (self.bit_width + 63) // 64

	@property
	def num_sample(self) -> int:
		return 0 if self.timestamps is None else self.timestamps.size

class ModuleData:
	children : List[Self]
	module_name : str
	signals : List[SignalData]

	def __init__(self, module_name):
		self.children = list()
		self.signals = list()
		self.module_name = module_name

class HierarchyTreeNode:
	parent : Optional[Self]
	nth_child : int
	module_data : ModuleData

	def __init__(self, module_name : str = str()):
		self.parent = None
		self.nth_child = 0
		self.module_data = ModuleData(module_name)

	def AddChild(self, module_name : str) -> Self:
		child = HierarchyTreeNode(module_name)
		child.parent = self
		child.nth_child = len(self.module_data.children)
		self.module_data.children.append(child)
		return child

	def AddSignal(self, signal_name, bit_width) -> SignalData:
		sig = SignalData(signal_name, bit_width)
		self.module_data.signals.append(sig)
		return sig

def BuildTestTree() -> HierarchyTreeNode:
	root = HierarchyTreeNode()
	child1 = root.AddChild("1")
	child11 = child1.AddChild("a")
	child12 = child1.AddChild("c")
	child2 = root.AddChild("3")
	child3 = root.AddChild("5")
	child31 = child3.AddChild("w")
	child32 = child3.AddChild("y")
	sig = child1.AddSignal("sig1", 10)
	sig.SetTimestampsAndData([0,10,20,100], [1,2,3,4])
	sig = child1.AddSignal("sig2", 99)
	sig = child1.AddSignal("sig3", 1)
	sig.SetTimestampsAndData(range(100), [i&1 for i in range(100)])
	sig = child2.AddSignal("tmp1", 2)
	sig = child2.AddSignal("tmp2", 3)
	sig = child31.AddSignal("s1", 12)
	sig = child32.AddSignal("s2", 13)
	return root

def BuildTestSignal(max_time : int) -> List[SignalData]:
	ret = list()
	half_period = 1
	for i in range(5):
		duty = 1
		for j in range(5):
			duty *= 3
			period = half_period * (1+duty)
			sig = SignalData()
			clock_start = np.arange(0, period, max_time, dtype=np.uint64)
			sig.timestamps = (
				np.vstack((clock_start, clock_start+period)).reshape((-1,), order='F')
			)
			ret.append(sig)
		half_period *= 3
	return ret
