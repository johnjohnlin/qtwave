from waveform.waveformloader_c import ParseFstWaveform, ParseVcdWaveform
import numpy as np
class SignalData(object):
	# TODO: 64+ bit signal
	# TODO: Data write

	@staticmethod
	def GetConstantsFromNbit(nbit, dtype):
		if nbit == 1:
			rshamt = 3
		elif nbit == 2:
			rshamt = 2
		elif nbit <= 4:
			rshamt = 1
		else:
			rshamt = 0
		mask = dtype.type(-1) >> dtype.type(8*dtype.itemsize - nbit)
		return rshamt, mask

	def __init__(self, tup):
		(
			self.nbit_, self.nsample_, self.timepoints_,
			self.data01_, self.dataxz_
		) = tup
		(
			self.kRSHAMT_, self.kMASK_
		) = SignalData.GetConstantsFromNbit(self.nbit_, self.data01_.dtype)

	def __getitem__(self, i):
		# Convert i to the numpy array index.
		# Shift 1/2/34-bits signals by 3/2/1, respectively.
		# Signals shorter than 4-bit are packed in a uint8.
		array_idx = i >> self.kRSHAMT_
		# Shift amount to extract the bits inside a uint8.
		# Type conversion is for preventing casting.
		rshamt = self.data01_.dtype.type((i << 3 >> self.kRSHAMT_) & 0x7)
		return (
			self.timepoints_[i],
			(self.data01_[array_idx] >> rshamt) & self.kMASK_,
			None if self.dataxz_ is None else (self.dataxz_[array_idx] >> rshamt) & self.kMASK_,
		)

	def GetValuesFromTimepoints(self, timepoints):
		assert timepoints.ndim == 1 and timepoints.size > 0 and (timepoints[1:] - timepoints[:-1] >= 0).all()
		i = np.searchsorted(self.timepoints_, timepoints, side='right')
		# 0 means the timepoint appears before the first sample, so prepend = 0 remove the sample
		nonzero_timepoints_bool = np.diff(i, prepend=0) != 0
		# return the x-axis (in pixel) where the signal changes
		nonzero_timepoints = np.nonzero(nonzero_timepoints_bool)[0]
		i = i[nonzero_timepoints_bool]
		i -= 1
		assert (i >= 0).all()
		return (nonzero_timepoints, *self.__getitem__(i))

class SignalHierarchy(object):
	def __init__(self, parent, signal_data, htyp, styp=0, name=str()):
		self.row_ = 0 if parent is None else len(parent.module_children_)
		self.parent_ = parent
		self.name_ = name
		self.hier_type_ = htyp
		self.secondary_type_ = styp
		self.module_children_ = list()
		self.signal_children_ = list()
		self.signal_data_ = signal_data

	@property
	def is_root_(self):
		return self.hier_type_ == -1

	@staticmethod
	def FromHierarchyCommand(hier_cmds, signal_data):
		root = SignalHierarchy(None, None, -1) # -1 for root
		st = [root]
		for hier_type, secondary_type, sig_idx, name in hier_cmds:
			if hier_type == 0: # FST_HT_SCOPE
				child = SignalHierarchy(
					st[-1], None, hier_type, secondary_type, name
				)
				st[-1].module_children_.append(child)
				st.append(child)
			elif hier_type == 1: # FST_HT_UPSCOPE
				st.pop()
			elif hier_type == 2: # FST_HT_VAR
				st[-1].signal_children_.append(SignalHierarchy(
					st[-1], signal_data[sig_idx], hier_type, secondary_type, name
				))
		return st[0]

class Waveform(object):
	def __init__(self, fname):
		(
			self.timescale_, self.max_timepoint_,
			hier_cmd, signal_data
		) = ParseFstWaveform(fname)
		self.signal_data_ = {k: SignalData(v) for k, v in signal_data.items()}
		self.root_ = SignalHierarchy.FromHierarchyCommand(hier_cmd, self.signal_data_)