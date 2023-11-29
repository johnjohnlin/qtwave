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
//	kIndexNoChange = -2u // signal is the same
};

class Timestamps {
	typedef std::vector<int64_t> TimeVec;
	// usually store the changing timestamps in waveform
	TimeVec timestamps_;

public:

	// rule of five
	Timestamps() = default;
	Timestamps(const Timestamps &other) = default;
	Timestamps(Timestamps &&other) = default;
	Timestamps &operator=(const Timestamps &other) = default;
	Timestamps &operator=(Timestamps &&other) = default;

	// trivial constructors
	Timestamps(const TimeVec& src) : timestamps_(src) {}
	Timestamps(TimeVec&& src) { std::swap(src, timestamps_); }
	Timestamps operator=(const TimeVec& src) { timestamps_ = src; return *this; }
	Timestamps operator=(TimeVec&& src) { std::swap(src, timestamps_); return *this; }

	// linear uniform spacing samples
	Timestamps(const float begin_, const float end_, const unsigned size) {
		SampleFromScreenspace(begin_, end_, size);
	}
	void SampleFromScreenspace(const float begin_, const float end_, const unsigned size) {
		timestamps_.resize(size);
		const float norm = (end_-begin_) / size;
		for (unsigned i = 0; i < size; ++i) {
			timestamps_[i] = int64_t(begin_ + float(i) * norm);
		}
	}

	// STL-like getters
	TimeVec& Get() { return timestamps_; }
	const TimeVec& Get() const { return timestamps_; }
	size_t Size() const { return timestamps_.size(); }
	int64_t& operator[](unsigned i) { return timestamps_[i]; }
	int64_t operator[](unsigned i) const { return timestamps_[i]; }

	void AddTimestamp(int64_t t) {
		CHECK(timestamps_.empty() or t > timestamps_.back());
		timestamps_.push_back(t);
	}

	void SampleIndex(
		const Timestamps& screenspace, // screenspace timestamps
		std::vector<unsigned>& indices // The index for indexing this->timestamps_
	) const;

	void GetIndexTimestamps(
		const std::vector<unsigned>& indices,
		Timestamps& sampled
	) const;

	void SampleIndexAndTime(
		const Timestamps& screenspace,
		std::vector<unsigned>& indices,
		Timestamps& sampled
	) const {
		SampleIndex(screenspace, indices);
		GetIndexTimestamps(indices, sampled);
	}
};

// Struct for launching
struct TimestampSampleEntry {
	const Timestamps* waveform;
	std::vector<unsigned> indices;
	Timestamps* sampled;
};

void SampleIndexAndTimeWithDumpoff(
	const Timestamps& screenspace,
	const Timestamps& dumpoff, // timestamps $dumpoff is called
	std::vector<TimestampSampleEntry> sample_entries // multiple signals in VCD
);

} // namespace waveform
