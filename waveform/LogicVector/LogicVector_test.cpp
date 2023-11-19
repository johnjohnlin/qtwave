// Direct include
// C system headers
// C++ standard library headers
// Other libraries' .h files.
#include <gtest/gtest.h>
// Your project's .h files.
#include "LogicVector/LogicVector.h"

using namespace std;
using namespace waveform;

TEST(LogicVector_test, PackedWord) {
	LogicVector logics[4]{
		CreateLogicVector(1),
		CreateLogicVector(2),
		CreateLogicVector(3),
		CreateLogicVector(4)
	};
	for (unsigned i = 0; i < 4; ++i) {
		EXPECT_EQ(logics[i]->NumBits(), i+1);
	}

	// 1-bit
	{
		auto& l = logics[0];
		vector<unsigned> idx{0};
		vector<LogicU64> ans(2);

		l->Append("1", 1);
		l->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 1);

		idx.push_back(1);
		l->Append("z", 1);
		l->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 1);
		EXPECT_EQ(ans[1].hi, 1);
		EXPECT_EQ(ans[1].lo, 1);
	}

	// 2-bit
	{
		auto& l = logics[1];
		vector<unsigned> idx{0};
		vector<LogicU64> ans(2);

		l->Append("10", 2);
		l->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 2);

		idx.push_back(1);
		l->Append("xz", 2);
		l->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 2);
		EXPECT_EQ(ans[1].hi, 3);
		EXPECT_EQ(ans[1].lo, 1);
	}

	// 3-bit
	{
		auto& l = logics[2];
		vector<unsigned> idx{0};
		vector<LogicU64> ans(2);

		l->Append("010", 3);
		l->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 2);

		idx.push_back(1);
		l->Append("1xz", 3);
		l->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 2);
		EXPECT_EQ(ans[1].hi, 3);
		EXPECT_EQ(ans[1].lo, 5);
	}

	// 4-bit
	{
		auto& l = logics[3];
		vector<unsigned> idx{0};
		vector<LogicU64> ans(2);

		l->Append("0011", 4);
		l->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 3);

		idx.push_back(1);
		l->Append("01xz", 4);
		l->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 3);
		EXPECT_EQ(ans[1].hi, 3);
		EXPECT_EQ(ans[1].lo, 5);
	}
}


TEST(LogicVector_test, OneWord) {
	LogicVector logic12 = CreateLogicVector(12);
	EXPECT_EQ(logic12->NumBits(), 12);

	logic12->Append("0 useless characters", 1);
	logic12->Append("1111000011110000", 16);
	{
		// No xz values
		const vector<unsigned> idx{0,1};
		vector<LogicU64> ans(2);
		logic12->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 0);
		EXPECT_EQ(ans[1].hi, 0);
		EXPECT_EQ(ans[1].lo, 0xf0f);
	}

	logic12->Append("0011xxzz", 8);
	{
		const vector<unsigned> idx{0,1,2};
		vector<LogicU64> ans(3);
		logic12->MultiIndex(idx.data(), ans.data(), idx.size());
		EXPECT_EQ(ans[0].hi, 0);
		EXPECT_EQ(ans[0].lo, 0);
		EXPECT_EQ(ans[1].hi, 0);
		EXPECT_EQ(ans[1].lo, 0xf0f);
		EXPECT_EQ(ans[2].hi, 0xf);
		EXPECT_EQ(ans[2].lo, 0x33);
	}
}
