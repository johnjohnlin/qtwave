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

enum class LogicValue {
	e0 = 0,
	e1 = 1,
	ex = 2,
	ez = 3
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
