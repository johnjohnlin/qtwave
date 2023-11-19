#pragma once
// Direct include
// C system headers
// C++ standard library headers
#include <memory>
#include <string_view>
#include <vector>
// Other libraries' .h files.
// Your project's .h files.
#include "LogicVector/detail/LogicString.h"

namespace waveform {

struct LogicVectorBase {
	virtual void Append(
		const char* str, // [N]
		const unsigned N
	) = 0;
	virtual void MultiIndex(
		const unsigned *idx, // [N]
		LogicU64 *data, // [N*NumU64()]
		const unsigned N
	) const = 0;
	virtual unsigned Size() const = 0;
	virtual unsigned NumBits() const = 0;
	virtual ~LogicVectorBase() {}
	unsigned NumU64() { return NumBits()+63/64; }
};

typedef std::unique_ptr<LogicVectorBase> LogicVector;
static LogicVector CreateLogicVector(unsigned num_bit);

} // namespace waveform
