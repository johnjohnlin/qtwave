// Direct include
#include "logic_vector/detail/HasTimestamps.h"
// C system headers
// C++ standard library headers
#include <algorithm>
// Other libraries' .h files.
// Your project's .h files.

namespace waveform {
using namespace std;

void HasTimestamps::SampleTimestampIndex(
	const std::vector<uint64_t>& timestamps_screenspace,
	std::vector<unsigned>& indices
) {
	// rename variables for clarity
	const auto& timestamps_waveform = timestamps_;
	// reset output
	indices.resize(0);
	// special case 1
	if (timestamps_screenspace.empty()) {
		// if there is nothing to be sampled at all.
		return;
	}
	// special case 2
	if (timestamps_waveform.empty()) {
		// if there is no value change at all.
		indices.assign(timestamps_screenspace.size(), kIndexOff);
		return;
	}

	// iterate all elements in screen space
	auto       ss_it = timestamps_screenspace.begin();
	const auto ss_end = timestamps_screenspace.end();
	auto       wf_left = timestamps_waveform.begin();
	const auto wf_begin = timestamps_waveform.begin(),
	           wf_right = timestamps_waveform.end();
	while (true) {
		DCHECK(ss_it != ss_end);
		wf_left = upper_bound(wf_left, wf_right, *ss_it);
		const bool is_dumpoff = (
			wf_left == wf_begin or
			binary_search(
				dumpoff_timestamps_.begin(),
				dumpoff_timestamps_.end(),
				*(wf_left-1)
			)
		);
		const unsigned wf_idx = wf_left - wf_begin - 1;
		bool is_first = true;
		while (true) {
			if (ss_it == ss_end) {
				return;
			}
			if (not (wf_left == wf_right or *ss_it < *wf_left)) {
				break;
			}
			indices.push_back(
				is_dumpoff ? kIndexOff :
				is_first ? wf_idx :
				kIndexNoChange
			);
			LOG(INFO) << indices.back();
			is_first = false;
			++ss_it;
		}
	}
}

} // namespace waveform
