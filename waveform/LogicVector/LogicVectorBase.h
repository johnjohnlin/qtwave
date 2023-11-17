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
	virtual void Index(
		const unsigned idx,
		LogicU64 *data // [NumU64()]
	) const = 0;
	virtual unsigned Size() const = 0;
	virtual unsigned NumBits() const = 0;
	virtual ~LogicVectorBase() {}

	// This one is not virtual
	unsigned NumU64() const { return (NumBits()+63)/64; }

	// This one has default implementation
	virtual void MultiIndex(
		const unsigned *idx, // [N]
		LogicU64 *data, // [N*NumU64()]
		const unsigned N
	) const {
		const unsigned num_u64 = NumU64();
		for (unsigned i = 0; i < N; ++i) {
			Index(idx[i], data);
			data += num_u64;
		}
	}
};

typedef std::unique_ptr<LogicVectorBase> LogicVector;
static LogicVector CreateLogicVector(unsigned num_bit);

} // namespace waveform
