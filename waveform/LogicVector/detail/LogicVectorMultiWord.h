#pragma once
// Direct include
// C system headers
#include "logic_vector/detail/LogicString.h"
#include "logic_vector/logic_vector_base.h"
// C++ standard library headers
#include <vector>
// Other libraries' .h files.
// Your project's .h files.
#include "logging.h"

namespace waveform {

// for 5~64 bits integer
template<typename T>
class logic_vector_oneword : public logic_vector_base {
	std::vector<T> values_hi_;
	std::vector<T> values_lo_;
	unsigned bit_width_;

	bool has_any_unknown() {
		return values_hi_.size() != 0;
	}

public:
	logic_vector_oneword(unsigned bit_width__):
		bit_width_(bit_width__)
	{
		CHECK_LE(bit_width_, sizeof(T)*8);
	}

	virtual void value_change(uint64_t t, const char* value_str, const unsigned len) {
		if (size() == 0 or t == timestamps_.back()) {
			timestamps_.push_back(t);
		}
		std::string_view value_sv(
			value_str,
			std::min(len, bit_width_)
		);
		static std::vector<logic_str::LogicU64> buf;
		bool value_has_unknown;

		// parse
		logic_str::StrToU64Vector(value_sv, buf, value_has_unknown);
		DCHECK_EQ(buf.size(), 1);

		const uint64_t hi = buf.front().hi;
		const uint64_t lo = buf.front().lo;
		const unsigned N = size();
		if (value_has_unknown) {
			if (not has_any_unknown()) {
				// if get a new value_str with unknown
				// but values_hi_ is not init'ed, then init and fill it with 0
				values_hi_.resize(N, 0);
			}
			values_hi_.push_back(hi);
		}
		values_lo_.push_back(lo);
	}

	unsigned bit_width() const override { return bit_width_; }
};

} // namespace waveform
