// Direct include
#include "LogicVector/detail/LogicString.h"
// C system headers
// C++ standard library headers
#include <vector>
// Other libraries' .h files.
#include <gtest/gtest.h>
using namespace std;
using namespace waveform;

TEST(LogicString_test, Test) {
	std::vector<LogicU64> u64_vec;
	bool has_unknown;

	StrToU64Vector(
		"00111100" "11001100",
		u64_vec,
		has_unknown
	);
	EXPECT_FALSE(has_unknown);
	ASSERT_EQ(u64_vec.size(), 1);
	EXPECT_EQ(u64_vec[0].hi, 0);
	EXPECT_EQ(u64_vec[0].lo, 0x3cccu);

	StrToU64Vector(
		"00zzxx00" "00zzxx00"
		"00000000" "00000000"
		"00000000" "00000000"
		"00000000" "00000000"
		"00zzxx00" "11001100",
		u64_vec,
		has_unknown
	);
	EXPECT_TRUE(has_unknown);
	ASSERT_EQ(u64_vec.size(), 2);
	EXPECT_EQ(u64_vec[1].hi, 0x3c3cu);
	EXPECT_EQ(u64_vec[1].lo, 0x3030u);
	EXPECT_EQ(u64_vec[0].hi, 0x3c00u);
	EXPECT_EQ(u64_vec[0].lo, 0x30ccu);
}
