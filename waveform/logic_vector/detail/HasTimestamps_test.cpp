// Direct include
#include "logic_vector/detail/HasTimestamps.h"
// C system headers
// C++ standard library headers
#include <vector>
// Other libraries' .h files.
#include <gtest/gtest.h>
// Your project's .h files.

using namespace std;
using namespace waveform;

constexpr uint64_t kDumpOff = -1;

static void ReplayDump(
	const vector<uint64_t>& replay,
	HasTimestamps& dut
) {
	for (unsigned i = 0; i < replay.size(); ++i) {
		if (replay[i] == kDumpOff) {
			++i;
			dut.Dumpoff(replay[i]);
		} else {
			dut.Dump(replay[i]);
		}
	}
}

TEST(HasTimestamps_test, Normal) {
	constexpr unsigned kNumTest = 4;
	const vector<uint64_t> ts_waveforms[kNumTest] {
		{10u, 23u, 25u, 26u, 27u, 39u, kDumpOff, 41u},
		{10u, 23u, 25u, 26u, 27u, 39u, kDumpOff, 40u},
		{5u, kDumpOff, 9u, 31u, kDumpOff, 60u},
		{0u, kDumpOff, 9u, 30u, 31u, kDumpOff, 49u}
	};
	const vector<unsigned> golds[kNumTest] {
		{kIndexOff, 0, kIndexNoChange, 4, 5, kIndexOff},
		{kIndexOff, 0, kIndexNoChange, 4, kIndexOff, kIndexOff},
		{kIndexOff, kIndexOff, kIndexOff, kIndexOff, 2, kIndexNoChange},
		{0, kIndexOff, kIndexOff, 2, 3, kIndexOff}

	};
	const vector<uint64_t> ts_screenspace{0, 10, 20, 30, 40, 50};

	for (unsigned test_id = 0; test_id < kNumTest; ++test_id) {
		HasTimestamps dut;
		ReplayDump(ts_waveforms[test_id], dut);
		vector<unsigned> ans;
		dut.SampleTimestampIndex(ts_screenspace, ans);

		auto& gold = golds[test_id];
		ASSERT_EQ(ans.size(), gold.size());
		for (unsigned i = 0; i < ans.size(); ++i) {
			EXPECT_EQ(ans[i], gold[i]) << "Test " << test_id << ", " << i << "-th element";
		}
	}
}

TEST(HasTimestamps_test, Boundary) {
	HasTimestamps dut;
	vector<uint64_t> ts{1,2,3,4};
	vector<uint64_t> ts_empty;
	vector<unsigned> ans;

	// 1. waveform is empty, screenspace is empty
	ans.resize(1); // fill answer as garbage
	dut.SampleTimestampIndex(ts_empty, ans);
	// answer is empty
	EXPECT_TRUE(ans.empty());

	// 2. waveform is empty, screenspace is not empty
	ans.resize(1); // fill answer as garbage
	dut.SampleTimestampIndex(ts, ans);
	// answer is all kIndexOff
	EXPECT_EQ(ans.size(), 4);
	auto first_non_off = find_if(ans.begin(), ans.end(), [](unsigned x){
		return x != kIndexOff;
	});
	EXPECT_TRUE(first_non_off == ans.end());

	dut.Dump(1);
	dut.Dump(2);
	// 3. waveform is not empty, screenspace is empty
	ans.resize(1); // fill answer as garbage
	dut.SampleTimestampIndex(ts_empty, ans);
	// answer is empty
	EXPECT_TRUE(ans.empty());
}
