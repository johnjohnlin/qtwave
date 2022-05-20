#include "waveform.h"
#include <cstring>
#include <iostream>
#include <memory>
using namespace std;

/**
	\brief Handle 1~4-bit signals.
*/
struct SignalData::DataS: public SignalData::Data {
	DataS(int nbit):
		Data(nbit),
		kMASK_((1<<nbit_)-1),
		kSHIFT_((nbit_ == 3) ? 4 : nbit_),
		cur_shift_(0),
		cur_sample_buf01_(0),
		cur_sample_bufxz_(0)
	{
	}
	virtual void PackBit(const int bit01, const int bitxz) {
		cur_sample_buf01_ <<= 1;
		cur_sample_bufxz_ <<= 1;
		cur_sample_buf01_ |= bit01 & 1;
		cur_sample_bufxz_ |= bitxz & 1;
	}
	virtual void FinishOneSample() {
		cur_sample_buf01_ &= kMASK_;
		cur_sample_bufxz_ &= kMASK_;
		if (cur_shift_ == 0) {
			data01_.push_back(0);
			dataxz_.push_back(0);
		}
		data01_.back() |= (cur_sample_buf01_ << cur_shift_) ;
		dataxz_.back() |= (cur_sample_bufxz_ << cur_shift_) ;
		cur_shift_ += kSHIFT_;
		cur_shift_ %= 8 * sizeof(uint8_t);
		cur_sample_buf01_ = 0;
		cur_sample_bufxz_ = 0;
	}
	virtual size_t get_vector_type_size() {
		return sizeof(uint8_t);
	}
	virtual size_t get_vector_size() {
		return data01_.size();
	}
	virtual void get_vector_pointers(const char* &ptr01, const char* &ptrxz) {
		ptr01 = reinterpret_cast<char*>(data01_.data());
		ptrxz = reinterpret_cast<char*>(dataxz_.data());
	}
	virtual ~DataS() {}
private:
	const int kMASK_, kSHIFT_;
	int cur_shift_;
	uint8_t cur_sample_buf01_, cur_sample_bufxz_;
	vector<uint8_t> data01_, dataxz_;
};

/**
	\brief Handle 5~64-bit signals.
*/
template<class T>
struct SignalData::DataM: public SignalData::Data {
	DataM(int nbit):
		Data(nbit),
		cur_sample_buf01_(0),
		cur_sample_bufxz_(0) {}
	virtual void PackBit(const int bit01, const int bitxz) {
		cur_sample_buf01_ <<= 1;
		cur_sample_bufxz_ <<= 1;
		cur_sample_buf01_ |= bit01 & 1;
		cur_sample_bufxz_ |= bitxz & 1;
	}
	virtual void FinishOneSample() {
		const int kSHIFT = 8*sizeof(T) - nbit_;
		// Clear the overflow LSBs
		cur_sample_buf01_ = (cur_sample_buf01_ << kSHIFT) >> kSHIFT;
		cur_sample_bufxz_ = (cur_sample_bufxz_ << kSHIFT) >> kSHIFT;
		data01_.push_back(cur_sample_buf01_) ;
		dataxz_.push_back(cur_sample_bufxz_) ;
		cur_sample_buf01_ = 0;
		cur_sample_bufxz_ = 0;
	}
	virtual size_t get_vector_type_size() {
		return sizeof(T);
	}
	virtual size_t get_vector_size() {
		return data01_.size();
	}
	virtual void get_vector_pointers(const char* &ptr01, const char* &ptrxz) {
		ptr01 = reinterpret_cast<char*>(data01_.data());
		ptrxz = reinterpret_cast<char*>(dataxz_.data());
	}
	virtual ~DataM() {}
private:
	T cur_sample_buf01_, cur_sample_bufxz_;
	vector<T> data01_, dataxz_;
};
template struct SignalData::DataM<uint8_t>;
template struct SignalData::DataM<uint16_t>;
template struct SignalData::DataM<uint32_t>;
template struct SignalData::DataM<uint64_t>;

/**
	\brief Handle 64+-bit signals.
*/
struct SignalData::DataL: public SignalData::Data  {
	DataL(int nbit):
		Data(nbit) {}
	virtual void PackBit(const int bit01, const int bitxz) {
		cerr << "64+ bit not implemented" << endl;
		abort();
	}
	virtual void FinishOneSample() {
		cerr << "64+ bit not implemented" << endl;
		abort();
	}
	virtual size_t get_vector_type_size() {
		return sizeof(uint64_t);
	}
	virtual size_t get_vector_size() {
		return data01_.size();
	}
	virtual void get_vector_pointers(const char* &ptr01, const char* &ptrxz) {
		ptr01 = reinterpret_cast<char*>(data01_.data());
		ptrxz = reinterpret_cast<char*>(dataxz_.data());
	}
private:
	vector<uint64_t> data01_, dataxz_;
};

SignalData::SignalData(const int nbit) {
	if (nbit <= 4) {
		data_.reset(new DataS(nbit));
	} else if (nbit <= 8) {
		data_.reset(new DataM<uint8_t>(nbit));
	} else if (nbit <= 16) {
		data_.reset(new DataM<uint16_t>(nbit));
	} else if (nbit <= 32) {
		data_.reset(new DataM<uint32_t>(nbit));
	} else if (nbit <= 64) {
		data_.reset(new DataM<uint64_t>(nbit));
	} else {
		data_.reset(new DataL(nbit));
	}
}

void SignalData::Pack4ValueBinaryString(uint64_t t, const char *s, int len) {
	timepoint_.push_back(t);
	if (len == -1) {
		len = strlen(s);
	}
	len = std::min<int>(data_->nbit_, len);
	for (int i = 0; i < len; ++i) {
		int b01 = 0, bxz = 0;
		switch (s[i]) {
			case '0': { b01 = 0; bxz = 0; break; }
			case '1': { b01 = 1; bxz = 0; break; }
			case 'x': { b01 = 0; bxz = 1; break; }
			default : { b01 = 1; bxz = 1; break; }
		}
		data_->PackBit(b01, bxz);
	}
	data_->FinishOneSample();
}