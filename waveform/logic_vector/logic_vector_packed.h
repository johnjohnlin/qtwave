#pragma once
#include "logic_vector/logic_vector_base.h"
#include "logging.h"

namespace waveform {

// for 1~4 bits integer
class logic_vector_packed : public logic_vector_base {
	std::vector<uint8_t> values_lo_;
	std::vector<uint8_t> values_hi_;
	unsigned bit_width_;
public:
	logic_vector_packed(unsigned bit_width__):
		bit_width_(bit_width__)
	{

	}

	unsigned bit_width() const override { return bit_width_; }
	virtual ~logic_vector_packed() {}
};

} // namespace waveform
