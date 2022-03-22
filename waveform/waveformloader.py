from waveformloader_c import ParseFstWaveform, ParseVcdWaveform
import numpy as np
class SignalData(object):
	def __init__(self, tup):
		(
			self.nbit_, self.nsample_, self.timepoints_,
			self.data01_, self.dataxz_
		) = tup
#		self.to_array_idx_shamt_ = 
#
#	def __getitem__(self, i):
#		array_idx = i >> self.to_array_idx_shamt_
#		return (
#			self.timepoints_[i],
#			np.right_shift(self.data01_[array_idx], >> ) & self.mask_
#			np.right_shift(self.dataxz_[array_idx], >> ) & self.mask_
#		)

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