#pragma once
#include "enums.h"
#include <cassert>
#include <cstdint>
#include <memory>
#include <unordered_map>
#include <string>
#include <vector>

class SignalData {
public:

	/**
		\brief A unified base helper class hold the data sample, using two vectors of uintX_t to hold the samples.

		- If the sample is 1-bit, then one uint8_t hold 8 samples,
		and the LSB in uint_8 is the earliest sample.
		- If the sample is 2/4-bit, then one uint8_t hold 4/2 samples,
		and the 2/4 LSBs in uint8_t are the earliest sample.
		- 3-bit samples are treated as 4-bit.
		- If the sample is within 5~64-bit, then use the minimum uintX_t type to hold one sample.
		- If the sample is larger then 64-bit, then use ceil(#bit, N) uint64_t to hold one sample.
		The LSB in the sample appears first.
	*/
	struct Data {
		int nbit_;
		Data(int nbit): nbit_(nbit) {}
		virtual void PackBit(const int bit01, const int bitxz) = 0;
		virtual void FinishOneSample() = 0;
		virtual size_t get_vector_type_size() = 0;
		virtual size_t get_vector_size() = 0;
		virtual void get_vector_pointers(const char* &ptr01, const char* &ptrxz) = 0;
		virtual ~Data() {}
	};
	class DataS;
	template <class T> class DataM;
	class DataL;
private:
	std::vector<uint64_t> timepoint_;
	std::unique_ptr<Data> data_;
public:
	SignalData(const int nbit);
	void Pack4ValueBinaryString(uint64_t t, const char *s, int len = -1);
	void Destroy() {
		timepoint_.clear();
		timepoint_.shrink_to_fit();
		data_.reset(nullptr);
	}
	int get_nbit() { return data_->nbit_; }
	size_t get_num_sample() { return timepoint_.size(); }
	uint64_t* get_timepoint_pointer() { return timepoint_.data(); }
	size_t get_vector_type_size() {
		return data_->get_vector_type_size();
	}
	size_t get_vector_size() {
		return data_->get_vector_size();
	}
	void get_vector_pointers(const char* &ptr01, const char* &ptrxz) {
		data_->get_vector_pointers(ptr01, ptrxz);
	}
};

struct HierarchyCommand {
	int hier_type_, secondary_type_;
	// Only for signals
	uint64_t signal_idx_;
	std::string name_;
};

struct Waveform {
	Waveform(): timescale_(0), max_timepoint_(0) {}
	std::vector<HierarchyCommand> hier_cmd_;
	int timescale_;
	uint64_t max_timepoint_;
	std::unordered_map<uint64_t, std::unique_ptr<SignalData>> signals_;
};