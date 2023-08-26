#pragma once
#include <cstddef>
#include <cstdint>
#include <vector>

namespace waveform {

class xz01vector_base {
	std::vector<uint64_t> timestamps;
	size_t size() const { return timestamps.size(); }

	virtual unsigned bit_width() const = 0;
	virtual ~xz01vector_base() {}
};

} // namespace waveform
