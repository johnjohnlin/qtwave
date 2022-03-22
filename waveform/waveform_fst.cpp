#inlcude "waveform_fst.h"

void fst_callback1(
	void *user_callback_data_pointer, uint64_t time, fstHandle handle,
	const unsigned char *value_str
) {
	auto waveform = static_cast<Waveform*>(user_callback_data_pointer);
	auto it = waveform->signals_.find(handle);
	if (it != waveform->signals_.end()) {
		it->second->Pack4ValueBinaryString(time, (const char*)value_str);
	}
}

void fst_callback2(
	void *user_callback_data_pointer, uint64_t time, fstHandle handle,
	const unsigned char *value_str, uint32_t len
) {
	auto waveform = static_cast<Waveform*>(user_callback_data_pointer);
	auto it = waveform->signals_.find(handle);
	if (it != waveform->signals_.end()) {
		it->second->Pack4ValueBinaryString(time, (const char*)value_str, len);
	}
}

int ParseFst(const char *file_name) {
	unique_ptr<Waveform> waveform(new Waveform);
	auto ctx = fstReaderOpen(file_name);
	if (ctx == nullptr) {
		return 1;
	}
	cout << "Timescale is " << +fstReaderGetTimescale(ctx) << endl;
	fstHier *hier;
	const char *cur_scope_name;
	fstReaderIterateHierRewind(ctx);
	while((hier = fstReaderIterateHier(ctx))) {
		switch (hier->htyp) {
			case FST_HT_SCOPE: {
				cur_scope_name = fstReaderPushScope(ctx, hier->u.scope.name, nullptr);
				cout << "Enter scope " << cur_scope_name << endl;
				break;
			}
			case FST_HT_UPSCOPE: {
				cur_scope_name = fstReaderPopScope(ctx);
				cout << "Leave scope " << cur_scope_name << endl;
				break;
			}
			case FST_HT_VAR: {
				auto &var = hier->u.var;
				auto it = waveform->signals_.insert(make_pair(
					uint64_t(var.handle),
					unique_ptr<SignalData>(new SignalData(var.length))
				));
				auto &inserted_or_existing = it.first->second;
				if (inserted_or_existing->nbit_ != var.length) {
					return 1;
				}
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

	for (const auto &kv: waveform->signals_) {
		cout << "Signal " << kv.first << endl;
		auto &signal = *kv.second;
		const int nbyte = (signal.nbit_+7)/8;
		for (int i = 0; i < signal.timepoint_.size(); ++i) {
			cout << "> Time " << dec << signal.timepoint_[i] << " 0x";
			for (int j = 0; j < nbyte; ++j) {
				cout << setfill('0') << setw(2) << hex <<
					+signal.data01_[nbyte*(i+1)-1-j];
			}
			cout << endl;
		}
	}
	return 0;
}

