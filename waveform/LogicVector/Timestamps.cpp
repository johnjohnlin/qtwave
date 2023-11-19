// Direct include
#include "LogicVector/Timestamps.h"
// C system headers
// C++ standard library headers
#include <algorithm>
// Other libraries' .h files.
// Your project's .h files.

namespace waveform {
using namespace std;

typedef vector<int64_t>::const_iterator IT;
static inline
IT upper_bound_optimized(IT first, IT last, unsigned val) {
	if (first != last and *first > val) {
		return first;
	}
	return upper_bound(first, last, val);
}

// Basically implement the searchedsort in numpy
void Timestamps::SampleIndex(
	const Timestamps& screenspace, // screenspace timestamps
	std::vector<unsigned>& indices // The index for indexing this->timestamps_
) const {
	const unsigned N = screenspace.timestamps_.size();
	indices.resize(N);
	auto begin_ = timestamps_.begin(),
	     left = timestamps_.begin(),
	     end_ = timestamps_.end();
	for (unsigned i = 0; i < N; ++i) {
		auto new_left = upper_bound_optimized(left, end_, screenspace.timestamps_[i]);
		const bool before_first_timestamp = new_left == begin_;
		indices[i] = (
			before_first_timestamp ?
			kIndexOff :
			(new_left - begin_ - 1)
		);
		left = new_left;
	}
}

void Timestamps::GetIndexTimestamps(
	const std::vector<unsigned>& indices,
	Timestamps& sampled
) const {
	sampled.timestamps_.resize(indices.size());
	for (unsigned i = 0; i < indices.size(); ++i) {
		if (indices[i] == kIndexOff) {
			continue;
		}
		sampled.timestamps_[i] = timestamps_[indices[i]];
	}
}

static void SetIndexOffByDumpoff(
	const Timestamps& dumpoff_sampled_,
	const Timestamps& sampled_,
	vector<unsigned>& indices
) {
	// extrace internal vectors
	auto& dumpoff_sampled = dumpoff_sampled_.Get();
	auto& waveform_sampled = sampled_.Get();
	// check size
	const unsigned N = indices.size();
	DCHECK_EQ(N, dumpoff_sampled.size());
	DCHECK_EQ(N, waveform_sampled.size());
	// Set waveform indices to kIndexOff
	// If dumpoff at 10, and waveform VCD change is 9,12,
	// For screenspace sample at 8,9,10,11,12,13
	// the resulting indices are Off,0,Off,Off,1,1
	for (unsigned i = 0; i < N; ++i) {
		if (dumpoff_sampled[i] >= waveform_sampled[i]) {
			indices[i] = kIndexOff;
		}
	}
}

void SampleIndexAndTimeWithDumpoff(
	const Timestamps& screenspace,
	const Timestamps& dumpoff, // timestamps $dumpoff is called
	const TimestampSampleEntry& sample_entry
) {
	std::vector<unsigned> dumpoff_indices;
	Timestamps dumpoff_sampled;
	dumpoff.SampleIndexAndTime(screenspace, dumpoff_indices, dumpoff_sampled);
	auto [waveform, indices, sampled] = sample_entry;
	waveform->SampleIndexAndTime(screenspace, *indices, *sampled);
	SetIndexOffByDumpoff(dumpoff_sampled, *sampled, *indices);
}

// Similar to SampleIndexAndTimeWithDumpoff, but batch mode
void BatchSampleIndexAndTimeWithDumpoff(
	const Timestamps& screenspace,
	const Timestamps& dumpoff, // timestamps $dumpoff is called
	const std::vector<TimestampSampleEntry>& sample_entries
) {
	std::vector<unsigned> dumpoff_indices;
	Timestamps dumpoff_sampled;
	dumpoff.SampleIndexAndTime(screenspace, dumpoff_indices, dumpoff_sampled);
	for (auto [waveform, indices, sampled]: sample_entries) {
		waveform->SampleIndexAndTime(screenspace, *indices, *sampled);
		SetIndexOffByDumpoff(dumpoff_sampled, *sampled, *indices);
	}
}

} // namespace waveform
