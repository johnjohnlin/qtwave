#include "waveform.h"
#include <cstring>
using namespace std;

void SignalData::Pack4ValueBinaryString(uint64_t t, const char *s, int len) {
	if (len == -1) {
		len = strlen(s);
	}
	len = std::min<int>(nbit_, len);
	timepoint_.push_back(t);
	uint8_t c01 = 0, cxz = 0;
	for (int i = 0; i < len; ++i) {
		uint8_t b01, bxz;
		switch (s[len-1-i]) {
			case '0': { b01 = 0<<7; bxz = 0<<7; break; }
			case '1': { b01 = 1<<7; bxz = 0<<7; break; }
			case 'x': { b01 = 0<<7; bxz = 1<<7; break; }
			default : { b01 = 1<<7; bxz = 1<<7; break; }
		}
		c01 = (c01>>1) | b01;
		cxz = (cxz>>1) | bxz;
		if (i % 8 == 7) {
			data01_.push_back(c01);
			dataxz_.push_back(cxz);
			c01 = 0;
			cxz = 0;
		}
	}
}

WaveNode* WaveNode::InsertChild(const string &s) {
	auto it_suc = children_.emplace(s, unique_ptr<WaveNode>());
	auto &uq_ptr = it_suc.first->second;
	if (not uq_ptr) {
		uq_ptr.reset(new WaveNode{this, nullptr});
	}
	return uq_ptr.get();
}