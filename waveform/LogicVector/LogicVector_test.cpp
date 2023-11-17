// Direct include
// C system headers
// C++ standard library headers
// Other libraries' .h files.
#include <gtest/gtest.h>
// Your project's .h files.
#include "LogicVector/LogicVector.h"

using namespace std;
using namespace waveform;

TEST(LogicVector_test, OneWord) {
	auto logic12 = CreateLogicVector(12);
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
