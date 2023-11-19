#pragma once
// Direct include
#include "LogicVector/detail/LogicVectorBase.h"
// C system headers
// C++ standard library headers
#include <cstdint>
#include <memory>
// Other libraries' .h files.
// Your project's .h files.
#include "logging.h"
#include "LogicVector/detail/LogicVectorPacked.h"
#include "LogicVector/detail/LogicVectorOneWord.h"
#include "LogicVector/detail/LogicVectorMultiWord.h"

namespace waveform {

static LogicVector CreateLogicVector(unsigned num_bit) {
	LogicVectorBase *ret = nullptr;
	if (num_bit <= 4) {
		ret = new LogicVectorPacked(num_bit);
	} else if (num_bit <= 8) {
		ret = new LogicVectorOneWord<uint8_t>(num_bit);
	} else if (num_bit <= 16) {
		ret = new LogicVectorOneWord<uint16_t>(num_bit);
	} else if (num_bit <= 32) {
		ret = new LogicVectorOneWord<uint32_t>(num_bit);
	} else if (num_bit <= 64) {
		ret = new LogicVectorOneWord<uint64_t>(num_bit);
	} else {
		ret = new LogicVectorOneWord<uint64_t>(num_bit);
		LOG(WARNING) << "[TODO] long integers are clamped to 64b";
	}
	CHECK(ret != nullptr) << num_bit << "-bit integer is not supported yet";
	return std::unique_ptr<LogicVectorBase>(ret);
}

} // namespace waveform
