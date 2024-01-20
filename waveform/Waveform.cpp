#pragma once
// Direct include
// C system headers
// C++ standard library headers
#include <vector>
// Other libraries' .h files.
#include "logging.h"
#include "fstapi.h"
// Your project's .h files.
#include "LogicVector/LogicVectorBase.h"
#include "LogicVector/Timestamps.h"
using namespace std;

namespace waveform {

// This is a humble wrapper for Timestamps and LogicVcetor
class Signal {
	LogicVector logic_;
	Timestamps timestamps_;
public:
	Signal(unsigned num_bits):
		logic_(CreateLogicVector(num_bits))
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

void value_change_callback(
	void *user_callback_data_pointer,
	uint64_t time,
	fstHandle facidx,
	const unsigned char *value
) {
}

void value_change_callback_varlen(
	void *user_callback_data_pointer,
	uint64_t time,
	fstHandle facidx,
	const unsigned char *value,
	uint32_t len
) {
}

struct FSTReaderWrapper {
	struct CStruct {
	} cstruct;
	vector<Signal> signals;
	Timestamps dumpoff_timestamps;
	void *fst_ctx;

	void ParseHierarchy() {
		fstHier* hier;
		while ((hier = fstReaderIterateHier(fst_ctx)) != nullptr) {
			switch (hier->htyp) {
				case FST_HT_SCOPE: {
				}
				case FST_HT_UPSCOPE: {
				}
				case FST_HT_VAR: {
				}
				default: break;
			}
		}
	}

	void ParseSignal() {
		fstReaderSetFacProcessMaskAll(fst_ctx);
		fstReaderIterBlocks2(
			fst_ctx,
			value_change_callback,
			value_change_callback_varlen,
			nullptr,
			nullptr
		);
	}

	FSTReaderWrapper(const char* fname) {
		fst_ctx = CHECK_NOTNULL(fstReaderOpen(fname));
		ParseHierarchy();
		ParseSignal();
	}
	CStruct* GetCStruct() {
		return &cstruct;
	}
	~FSTReaderWrapper() {
		fstReaderClose(fst_ctx);
	}
};

} // namespace waveform

extern "C" {

waveform::FSTReaderWrapper* FSTReader_new(const char* fname) {
	return new waveform::FSTReaderWrapper(fname);
}

void FSTReader_delete(waveform::FSTReaderWrapper* fst_reader) {
	delete fst_reader;
}

}
