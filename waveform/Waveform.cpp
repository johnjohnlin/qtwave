// Direct include
// C system headers
// C++ standard library headers
#include <vector>
// Other libraries' .h files.
#include "logging.h"
#include "fst/fstapi.h"
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

struct HierCommand {
	uint8_t enums[4];
	HierCommand(uint8_t a = 0, uint8_t b = 0, uint8_t c = 0, uint8_t d = 0): enums{a,b,c,d} {}
};

struct HierScope {
	string name;
	string component;
};

struct HierVar {
	string name;
	bool is_alias;
};

struct CStruct {
};

class FSTReaderWrapper {
	CStruct cstruct;
	void *fst_ctx;

	struct {
		vector<HierCommand> commands;
		vector<HierScope> scopes;
		vector<HierVar> vars;
	} hier_;
	vector<Signal> signals;
	Timestamps dumpoff_timestamps;

	void ParseHierarchy() {
		fstHier* hier;
		while ((hier = fstReaderIterateHier(fst_ctx)) != nullptr) {
			switch (hier->htyp) {
				case FST_HT_SCOPE: {
					auto& scope = hier->u.scope;
				}
				case FST_HT_UPSCOPE: {
				}
				case FST_HT_VAR: {
					auto& var = hier->u.var;
				}
				default: {
					LOG(FATAL) << "Cannot recognize hierarchy type";
					break;
				}
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

public:
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
