// Direct include
#include "LogicVector/detail/LogicString.h"
// C system headers
// C++ standard library headers
// Other libraries' .h files.
// Your project's .h files.

namespace waveform {

static inline LogicValue CharToLogicValue(char c) {
	LogicValue ret;
	switch (c) {
		case '0': {
			ret = LogicValue::v0;
			break;
		}
		case '1': {
			ret = LogicValue::v1;
			break;
		}
		case 'x':
		case 'X': {
			ret = LogicValue::vx;
			break;
		}
		default: {
			ret = LogicValue::vz;
			break;
		}
	}
	return ret;
}

void StrToU64Vector(
	const std::string_view value_str,
	std::vector<LogicU64>& u64_vec,
	bool& has_unknown
) {
	const unsigned u64_len = std::max<unsigned>((value_str.size()+63)/64, 1);
	u64_vec.resize(u64_len);

	has_unknown = false;
	for (unsigned i = 0; i < value_str.size(); ++i) {
		const unsigned logic_char = value_str[value_str.size()-1-i];
		const unsigned logic_bit = CharToLogicValue(logic_char);
		const uint64_t logic_bit_hi = logic_bit>>1;
		const uint64_t logic_bit_lo = logic_bit&0x1;
		const unsigned word_position = i/64;
		const unsigned bit_position = i%64;
		LogicU64& logic_val = u64_vec[word_position];
		if (bit_position == 0) {
			logic_val.hi = 0;
			logic_val.lo = 0;
		}
		logic_val.hi |= logic_bit_hi << bit_position;
		logic_val.lo |= logic_bit_lo << bit_position;
		has_unknown |= bool(logic_bit_hi);
	}
}

} // namespace waveform
