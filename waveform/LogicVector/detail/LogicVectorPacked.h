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

// for 1~4 bits integer, 3-bit is considered as 4-bit
class LogicVectorPacked : public LogicVectorBase {
	std::vector<uint64_t> values_hi_;
	std::vector<uint64_t> values_lo_;
	const unsigned bit_width_;
	unsigned size_;
	unsigned inserting_shift_; // the bit position for inserting value

	const uint8_t bit_width_storage_() const {
		static const uint8_t table[4]{1,2,4,4};
		return table[bit_width_-1];
	}

	const uint8_t idx_shift_() const {
		static const uint8_t table[4]{6,5,4,4};
		return table[bit_width_-1];
	}

	const uint8_t value_mask_() const {
		return (1<<bit_width_)-1;
	}

	bool HasAnyUnknown() const {
		return not values_hi_.empty();
	}

	uint64_t AccessVector(const std::vector<uint64_t>& values, unsigned i) const {
		const uint8_t idx_shift = idx_shift_();
		const uint8_t value_mask = value_mask_();
		const unsigned i_word = i>>idx_shift;
		const unsigned i_subword = (i<<6>>idx_shift) & 0x1f;
		return (values[i_word] >> i_subword) & value_mask;
	}

	uint64_t AccessLo(const unsigned i) const {
		return AccessVector(values_lo_, i);
	}

	uint64_t AccessHi(unsigned i) const {
		return HasAnyUnknown() ? AccessVector(values_hi_, i) : uint64_t(0);
	}

public:

	LogicVectorPacked(unsigned bit_width):
		bit_width_(bit_width),
		size_(0),
		inserting_shift_(0)
	{
		DCHECK(0 < bit_width_ and bit_width_ <= 4) << bit_width_;
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
			if (inserting_shift_ == 0) {
				values_hi_.push_back(0);
			}
			values_hi_.back() |= hi << inserting_shift_;
		}
		if (inserting_shift_ == 0) {
			values_lo_.push_back(0);
		}
		values_lo_.back() |= lo << inserting_shift_;
		inserting_shift_ += bit_width_storage_();
		++size_;
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
			data->hi = AccessHi(i);
			data->lo = AccessLo(i);
		}
	}

	unsigned Size() const override {
		return size_;
	}

	unsigned NumBits() const override {
		return bit_width_;
	}

};

} // namespace waveform
