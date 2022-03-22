#include "fstapi.h"
#include "waveform.h"
#include "waveform_fst.h"
#include <cstdint>
#include <memory>
using namespace std;

static void fst_callback1(
	void *user_callback_data_pointer, uint64_t time, fstHandle handle,
	const unsigned char *value_str
) {
	auto waveform = static_cast<Waveform*>(user_callback_data_pointer);
	auto it = waveform->signals_.find(handle);
	if (it != waveform->signals_.end()) {
		it->second->Pack4ValueBinaryString(time, (const char*)value_str);
	}
}

static void fst_callback2(
	void *user_callback_data_pointer, uint64_t time, fstHandle handle,
	const unsigned char *value_str, uint32_t len
) {
	auto waveform = static_cast<Waveform*>(user_callback_data_pointer);
	auto it = waveform->signals_.find(handle);
	if (it != waveform->signals_.end()) {
		it->second->Pack4ValueBinaryString(time, (const char*)value_str, len);
	}
}

int ParseFst(const char *file_name, unique_ptr<Waveform> &waveform) {
	auto ctx = fstReaderOpen(file_name);
	if (ctx == nullptr) {
		return 1;
	}
	waveform.reset(new Waveform);
	waveform->timescale_ = fstReaderGetTimescale(ctx);
	auto &hier_cmd = waveform->hier_cmd_;
	fstHier *hier;
	fstReaderIterateHierRewind(ctx);
	while((hier = fstReaderIterateHier(ctx))) {
		switch (hier->htyp) {
			case FST_HT_SCOPE: {
				auto &scope = hier->u.scope;
				hier_cmd.push_back({hier->htyp, scope.typ});
				fstReaderPushScope(ctx, scope.name, nullptr);
				break;
			}
			case FST_HT_UPSCOPE: {
				hier_cmd.push_back({hier->htyp});
				fstReaderPopScope(ctx);
				break;
			}
			case FST_HT_VAR: {
				auto &var = hier->u.var;
				uint64_t signal_idx = var.handle;
				waveform->signals_.insert(make_pair(
					signal_idx,
					unique_ptr<SignalData>(new SignalData(var.length))
				));
				hier_cmd.push_back({hier->htyp, var.typ, signal_idx, var.name});
				break;
			}
		}
	}
	fstReaderClrFacProcessMaskAll(ctx);
	for (const auto &kv: waveform->signals_) {
		fstReaderSetFacProcessMask(ctx, fstHandle(kv.first));
	}
	fstReaderIterBlocks2(ctx, fst_callback1, fst_callback2, (void*)waveform.get(), nullptr);
	fstReaderClose(ctx);

	return 0;
}

