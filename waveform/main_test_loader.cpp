#include "waveform.h"
#include "waveform_fst.h"
#include <cstring>
#include <memory>
using namespace std;

int main(int argc, char **argv) {
	size_t flen = 0;
	if (argc == 2) {
		flen = strlen(argv[1]);
	}
	if (flen == 0) {
		return 1;
	}
	unique_ptr<Waveform> waveform;
	if (strcmp(argv[1]+flen-3, "fst")) {
		;
	}
	if (not waveform) {
		return 1;
	}
	return 0;
}
