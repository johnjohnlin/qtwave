from waveformloader_c import ParseFstWaveform, ParseVcdWaveform
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

class SignalHierarchy(object):
	def __init__(self, signal_data, htyp, styp=0, name=str()):
		self.name_ = name
		self.hier_type_ = htyp
		self.secondary_type_ = styp
		self.children_ = list()
		self.signal_data_ = signal_data

	@staticmethod
	def FromHierarchyCommand(hier_cmds, signal_data):
		root = SignalHierarchy(signal_data, -1) # -1 for root
		st = [root]
		for hier_type, secondary_type, sig_idx, name in hier_cmds:
			if hier_type == 0: # FST_HT_SCOPE
				child = SignalHierarchy(
					signal_data, hier_type, secondary_type, name
				)
				root.children_.append(child)
				st.append(child)
			elif hier_type == 1: # FST_HT_UPSCOPE
				st.pop()
			elif hier_type == 2: # FST_HT_VAR
				st[-1].children_.append(SignalHierarchy(
					signal_data, hier_type, secondary_type, name
				))
		return st[0]

class Waveform(object):
	def __init__(self, fname):
		self.timescale_, hier_cmd, signal_data = ParseFstWaveform(fname)
		self.signal_data_ = {k: SignalData(v) for k, v in signal_data.items()}
		self.hier_cmd_ = SignalHierarchy.FromHierarchyCommand(hier_cmd, self.signal_data_)

if __name__ == "__main__":
	import os
	fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_ahb_example.fst")
	wave = Waveform(fname)
	wave.signal_data_[3][4][0].dtype