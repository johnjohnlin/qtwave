// Direct include
#include "LogicVector/Timestamps.h"
// C system headers
// C++ standard library headers
#include <vector>
// Other libraries' .h files.
#include <gtest/gtest.h>
// Your project's .h files.

using namespace std;
using namespace waveform;

TEST(Sample_test, Normal) {
	constexpr unsigned kNumTest = 2;
	const vector<int64_t> ts_waveforms[kNumTest] {
		{10u, 23u, 25u, 26u, 27u, 39u, 41u},
		{0u, 9u, 30u, 31u, 49u}
	};
	const vector<unsigned> index_golds[kNumTest] {
		{kIndexOff, 0u, 0u, 4u, 5u, 6u},
		{0u, 1u, 1u, 2u, 3u, 4u},
	};
	const vector<int64_t> ts_golds[kNumTest] {
		{kIndexOff, 10u, 10u, 27u, 39u, 41u},
		{0u, 9u, 9u, 30u, 31u, 49u},
	};
	const Timestamps ts_screenspace = vector<int64_t>{0, 10, 20, 30, 40, 50};

	for (unsigned test_id = 0; test_id < kNumTest; ++test_id) {
		Timestamps ts_waveform(ts_waveforms[test_id]);
		Timestamps ts_ans;
		vector<unsigned> index_ans;
		ts_waveform.SampleIndexAndTime(ts_screenspace, index_ans, ts_ans);

		auto& index_gold = index_golds[test_id];
		auto& ts_gold = ts_golds[test_id];
		const unsigned N = index_ans.size();
		ASSERT_EQ(N, ts_ans.Size());
		ASSERT_EQ(N, index_gold.size());
		ASSERT_EQ(N, ts_gold.size());

		for (unsigned i = 0; i < N; ++i) {
			EXPECT_EQ(index_ans[i], index_gold[i]) << "Test " << test_id << ", " << i << "-th element";
			if (index_ans[i] != kIndexOff) {
				EXPECT_EQ(ts_ans[i], ts_gold[i]) << "Test " << test_id << ", " << i << "-th element";
			}
		}
	}
}

TEST(Sample_test, Boundary) {
	Timestamps ts_empty;
	Timestamps ts_nonempty = vector<int64_t>{1,2,3,4};
	vector<unsigned> ans;

	// 1. waveform is empty, screenspace is empty
	ans.resize(1); // fill answer as garbage
	ts_empty.SampleIndex(ts_empty, ans);
	// answer is empty
	EXPECT_TRUE(ans.empty());

	// 2. waveform is empty, screenspace is not empty
	ans.resize(1); // fill answer as garbage
	ts_empty.SampleIndex(ts_nonempty, ans);
	// answer is all kIndexOff
	EXPECT_EQ(ans.size(), ts_nonempty.Size());
	auto first_non_off = find_if(ans.begin(), ans.end(), [](unsigned x){
		return x != kIndexOff;
	});
	EXPECT_TRUE(first_non_off == ans.end());

	// 3. waveform is not empty, screenspace is empty
	ans.resize(1); // fill answer as garbage
	ts_nonempty.SampleIndex(ts_empty, ans);
	// answer is empty
	EXPECT_TRUE(ans.empty());
}

TEST(Sample_test, HandleDumpoff) {
	const Timestamps ts_dumpoff = vector<int64_t>{
		10u, 15u
	};
	const Timestamps ts_value_changes = vector<int64_t>{
		7u, 10u, 11u, 12u
	};
	const Timestamps ts_screenspace = vector<int64_t>{
		6u, 7u, 8u, 9u, 10u, 11u, 12u, 13u, 14u
	};
	const vector<unsigned> sample_indices_gold{
		kIndexOff, 0u, 0u, 0u, kIndexOff, 2u, 3u, 3u, 3u
	};
	constexpr unsigned DONT_CARE = -1u;
	const Timestamps sampled_timestamps_gold = vector<int64_t>{
		DONT_CARE, 7u, 7u, 7u, DONT_CARE, 11u, 12u, 12u, 12u
	};
	const unsigned N = ts_screenspace.Size();

	Timestamps sampled_timestamps_;
	vector<TimestampSampleEntry> entries_{{&ts_value_changes, {}, &sampled_timestamps_}};
	SampleIndexAndTimeWithDumpoff(ts_screenspace, ts_dumpoff, entries_);
	auto& sampled_timestamps = sampled_timestamps_.Get();
	EXPECT_EQ(entries_sampled_indices.size(), N);
	EXPECT_EQ(sampled_timestamps.size(), N);
	for (unsigned i = 0; i < N; ++i) {
		EXPECT_EQ(sample_indices_gold[i], sampled_indices[i]);
		if (sample_indices_gold[i] != kIndexOff) {
			EXPECT_EQ(sampled_timestamps_gold[i], sampled_timestamps[i]);
		}
	}
}
