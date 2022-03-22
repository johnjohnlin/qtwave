#pragma once
#include "waveform.h"
#include <memory>

int ParseFst(const char *file_name, std::unique_ptr<Waveform> &waveform);