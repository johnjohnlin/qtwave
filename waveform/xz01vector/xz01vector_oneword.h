#pragma once
#include "xz01vector_base.h"

namespace waveform {

class xz01vector_oneword : public xz01vector_base {
	xz01vector_oneword()

	virtual unsigned bit_width() const = 0;
	virtual ~xz01vector_oneword() {}
};

} // namespace waveform
