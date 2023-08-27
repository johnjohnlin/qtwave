#pragma once
// Direct include
// C system headers
// C++ standard library headers
#include <cstddef>
#include <cstdint>
#include <string_view>
#include <vector>
// Other libraries' .h files.
// Your project's .h files.

namespace waveform {

enum LogicValue : unsigned {
	v0 = 0,
	v1 = 1,
	vx = 2,
	vz = 3,
};

struct LogicU64 {
	uint64_t hi, lo;
};

void StrToU64Vector(
	const std::string_view value_str,
	std::vector<LogicU64>& u64_vec,
	bool& has_unknown
);

} // namespace waveform
