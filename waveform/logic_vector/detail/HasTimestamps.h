#pragma once
// Direct include
// C system headers
// C++ standard library headers
#include <cstddef>
#include <cstdint>
#include <vector>
// Other libraries' .h files.
// Your project's .h files.
#include "logging.h"

namespace waveform {

enum SpecialIndex: unsigned {
	kIndexOff = -1u, // vcd is turn-off'ed
	kIndexNoChange = -2u // signal is the same
};

struct HasTimestamps {
	std::vector<uint64_t> timestamps_;
	std::vector<uint64_t> dumpoff_timestamps_;

	size_t Size() const { return timestamps_.size(); }

	void Dump(uint64_t t) {
		CHECK(timestamps_.empty() or t > timestamps_.back());
		timestamps_.push_back(t);
	}

	void Dumpoff(uint64_t t) {
		CHECK(timestamps_.empty() or t > timestamps_.back());
		const bool is_already_off = (
			not dumpoff_timestamps_.empty() and
			dumpoff_timestamps_.back() > timestamps_.back()
		);
		if (is_already_off) {
			return;
		}
		timestamps_.push_back(t);
		dumpoff_timestamps_.push_back(t);
	}

	void SampleTimestampIndex(
		const std::vector<uint64_t>& timestamps_screenspace,
		std::vector<unsigned>& indices
	);
};

} // namespace waveform
