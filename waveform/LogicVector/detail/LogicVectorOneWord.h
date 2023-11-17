#pragma once
// Direct include
#include "LogicVector/detail/LogicVectorBase.h"
// C system headers
#include "LogicVector/detail/LogicString.h"
#include "LogicVector/Timestamps.h"
// C++ standard library headers
#include <vector>
// Other libraries' .h files.
// Your project's .h files.
#include "logging.h"

namespace waveform {

// for 5~64 bits integer
template<typename T>
class LogicVectorOneWord : public LogicVectorBase {
	std::vector<T> values_hi_;
	std::vector<T> values_lo_;
	unsigned bit_width_;

	bool HasAnyUnknown() const {
		return not values_hi_.empty();
	}

public:

	LogicVectorOneWord(unsigned bit_width):
		bit_width_(bit_width)
	{
		DCHECK_LE(bit_width_, sizeof(T)*8);
	}

	void Append(
		const char* str,
		const unsigned str_length_
	) override {
		const unsigned str_length = std::min(str_length_, bit_width_);
		std::string_view value_sv(str, str_length);
		static std::vector<LogicU64> buf;
		bool value_has_unknown;

		// parse
		StrToU64Vector(value_sv, buf, value_has_unknown);
		DCHECK_EQ(buf.size(), 1);

		const uint64_t hi = buf.front().hi;
		const uint64_t lo = buf.front().lo;
		if (value_has_unknown) {
			if (not HasAnyUnknown()) {
				// if get a new str with unknown
				// but values_hi_ is not init'ed, then init and fill it with 0
				values_hi_.resize(Size(), 0);
			}
			values_hi_.push_back(hi);
		}
		values_lo_.push_back(lo);
	}

	void MultiIndex(
		const unsigned *idx, // [N]
		LogicU64 *data, // [N*NumU64()]
		const unsigned N
	) const override {
		for (unsigned i = 0; i < N; ++i, ++data, ++idx) {
			if (*idx == kIndexOff) {
				continue;
			}
			data->hi = HasAnyUnknown() ? uint64_t(values_hi_[i]) : uint64_t(0);
			data->lo = values_lo_[i];
		}
	}

	unsigned Size() const override {
		return values_lo_.size();
	}

	unsigned NumBits() const override {
		return bit_width_;
	}

};

} // namespace waveform
