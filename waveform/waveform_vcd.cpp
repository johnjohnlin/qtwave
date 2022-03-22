#include "fstapi.h"
#include <cassert>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <memory>
#include <unordered_map>
#include <string>
#include <vector>
using namespace std;

enum vcdPackType: int {
	VCD_DECLARE_COMMENT        = 1,
	VCD_DECLARE_DATE           = 2,
	VCD_DECLARE_ENDDEFINITIONS = 3,
	VCD_DECLARE_SCOPE          = 4,
	VCD_DECLARE_TIMESCALE      = 5,
	VCD_DECLARE_UPSCOPE        = 6,
	VCD_DECLARE_VAR            = 7,
	VCD_DECLARE_VERSION        = 8
};

static const char SPACE_CHARS[] = " \t\f\v\n\r";
static const vector<vector<pair<string, int>>> declare_keywords{
	{
		{"$comment"       , VCD_DECLARE_COMMENT       },
		{"$date"          , VCD_DECLARE_DATE          },
		{"$enddefinitions", VCD_DECLARE_ENDDEFINITIONS},
		{"$scope"         , VCD_DECLARE_SCOPE         },
		{"$timescale"     , VCD_DECLARE_TIMESCALE     },
		{"$upscope"       , VCD_DECLARE_UPSCOPE       },
		{"$var"           , VCD_DECLARE_VAR           },
		{"$version"       , VCD_DECLARE_VERSION       }
	}
};
static const vector<vector<pair<string, int>>> scope_keywords{
	{
		{"begin"   , FST_ST_VCD_BEGIN   },
	},
	{
		{"fork"    , FST_ST_VCD_FORK    },
		{"function", FST_ST_VCD_FUNCTION},
	},
	{
		{"module"  , FST_ST_VCD_MODULE  },
	},
	{
		{"task"    , FST_ST_VCD_TASK    },
	}
};
static const vector<vector<pair<string, int>>> var_keywords{
	{
		{"event"    , FST_VT_VCD_EVENT    },
	},
	{
		{"integer"  , FST_VT_VCD_INTEGER  },
	},
	{
		{"parameter", FST_VT_VCD_PARAMETER},
	},
	{
		{"realtime" , FST_VT_VCD_REALTIME },
		{"real"     , FST_VT_VCD_REAL     },
		{"reg"      , FST_VT_VCD_REG      },
	},
	{
		{"supply0"  , FST_VT_VCD_SUPPLY0  },
		{"supply1"  , FST_VT_VCD_SUPPLY1  },
	},
	{
		{"time"     , FST_VT_VCD_TIME     },
		{"triand"   , FST_VT_VCD_TRIAND   },
		{"trior"    , FST_VT_VCD_TRIOR    },
		{"trireg"   , FST_VT_VCD_TRIREG   },
		{"tri0"     , FST_VT_VCD_TRI0     },
		{"tri1"     , FST_VT_VCD_TRI1     },
		{"tri"      , FST_VT_VCD_TRI      },
	},
	{
		{"wand"     , FST_VT_VCD_WAND     },
		{"wire"     , FST_VT_VCD_WIRE     },
		{"wor"      , FST_VT_VCD_WOR      },
	}
};

static void Strip(size_t &pos, string &s) {
	pos = s.find_first_not_of(SPACE_CHARS, pos);
	if (pos != string::npos) {
		const size_t tail = s.find_last_not_of(SPACE_CHARS);
		// This shall not happen since the string
		assert(tail != string::npos);
		s.resize(tail+1);
	} else {
		pos = s.size();
	}
}

static int ParseStart(
	size_t &pos, string &s,
	const vector<vector<pair<string, int>>> &keywords
) {
	if (pos == s.size()) {
		return -1;
	}
	// k is a keyword list consisted of the same starting character.
	for (auto &k: keywords) {
		if (k.empty() or k[0].first.empty() or s[pos] != k[0].first[0]) {
			continue;
		}
		for (auto &p: k) {
			const string &prefix = p.first;
			if (prefix.compare(0, prefix.size(), s, pos, prefix.size()) == 0) {
				pos += p.first.size();
				return p.second;
			}
		}
	}
	return -1;
}

static int ParseEndWord(
	size_t &pos, string &s,
	const string &keyword
) {
	if (
		pos+keyword.size() <= s.size() and
		keyword.compare(0, keyword.size(), s, s.size()-keyword.size(), keyword.size()) == 0
	) {
		s.resize(s.size() - keyword.size());
		Strip(pos, s);
		return 0;
	}
	return -1;
}

int ParseVcdStream(istream &ist) {
	static const string ENDW("$end");
	string line;
	size_t pos;
	constexpr int INIT = 0;
	int line_type = INIT;
	bool has_end, done = false;
	int remain = 0;
	int remain_list[]{0, 0, 0, 2, 2, 0, 4, 0};
	// For $timescale
	int timescale = 0;
	// For $scope and $upscope
	int scope_type;
	vector<pair<int, string>> scope_stack;
	// For $var
	int var_type, var_size;
	while (ist.good() and not done) {
		pos = 0;
		getline(ist, line);
		Strip(pos, line);
		if (pos == line.size()) {
			continue;
		}
		if (line_type == INIT) {
			line_type = ParseStart(pos, line, declare_keywords);
			remain = remain_list[line_type-1];
		}
		has_end = ParseEndWord(pos, line, ENDW) == 0;
		switch (line_type) {
			case 4: {
				scope_stack.emplace_back(0, "");
				switch (remain) {
					case 2: {
						Strip(pos, line);
						scope_type = ParseStart(pos, line, scope_keywords);
						--remain;
					}
					case 1: {
						Strip(pos, line);
						scope_stack.emplace_back(scope_type, string(line, pos));
						--remain;
					}
				}
				break;
			}
			case 5: {
				switch (remain) {
					case 2: {
						Strip(pos, line);
						if (pos < line.size() and line[pos] == '1') {
							timescale = 0;
							++pos;
							while (pos < line.size() and line[pos] == '0') {
								++timescale;
								++pos;
							}
						}
						--remain;
					}
					case 1: {
						Strip(pos, line);
						if (pos+2 == line.size()) {
							switch (line[pos]) {
								case 'm': { timescale -=  3; break; }
								case 'u': { timescale -=  6; break; }
								case 'n': { timescale -=  9; break; }
								case 'p': { timescale -= 12; break; }
								case 'f': { timescale -= 15; break; }
							}
						}
						cout << "Timescale is " << timescale << endl;
						--remain;
					}
				}
				break;
			}
			case 6: {
				scope_stack.pop_back();
				break;
			}
			case 7: {
				switch (remain) {
					case 4: {
						Strip(pos, line);
						var_type = ParseStart(pos, line, var_keywords);
						--remain;
					}
					case 3: {
						Strip(pos, line);
						size_t old_pos = pos;
						pos = line.find_first_of(" \t", pos);
						Strip(pos, line);
						--remain;
					}
					case 2: {
						Strip(pos, line);
						--remain;
					}
					case 1: {
						Strip(pos, line);
						--remain;
					}
				}
				break;
			}
		}
		if (has_end) {
			if (remain != 0) {
				return 1;
			}
			if (line_type == 3) {
				done = true;
			}
			line_type = INIT;
		}
	}
	return 0;
}

int ParseVcd(const char *file_name) {
	ifstream ifs(file_name, ifstream::in);
	return ParseVcdStream(ifs);
}


