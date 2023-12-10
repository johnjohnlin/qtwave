#pragma once
// Direct include
// C system headers
// C++ standard library headers
// Other libraries' .h files.
// Your project's .h files.
#include "LogicVector/LogicVectorBase.h"
#include "LogicVector/Timestamps.h"

namespace waveform {

// This is a humble wrapper for Timestamps and LogicVcetor
class Signal {
	LogicVector logic_;
	Timestamps timestamps_;
public:
	Signal(unsigned num_bits):
		logic_(std::move(CreateLogicVector(num_bits)))
	{
	}
	~Signal() {}
	unsigned Size() { return logic_->Size(); }
	unsigned NumBits() { return logic_->NumBits(); }
	unsigned NumU64() { return logic_->NumBits(); }

	void Append(
		int64_t timestamp,
		const char* str, // [N]
		const unsigned N
	) {
		timestamps_.AddTimestamp(timestamp);
		logic_->Append(str, N);
	}
};

struct FSTReaderWrapper {
	FSTReaderWrapper(const char* fname) {}
};
/*
static void WaveformSample(
	const Timestamps* screenspace,
	const Timestamps* dumpoff,
	vectorSignal
	const TimestampSampleEntry* sample_entries
) {
}
*/
extern "C" {

FSTReaderWrapper* FSTReaderNew(const char* fname) {
	return new FSTReaderWrapper(fname);
}

unsigned FSTReaderListHeaders() {
}

void FSTReaderDelete(FSTReaderWrapper* fst_reader) {
	delete fst_reader;
}

}

} // namespace waveform
