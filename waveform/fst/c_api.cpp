#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <utility>
#include <vector>
extern "C" {
#include "fstapi.h"
}

namespace py = pybind11;
using namespace std;

namespace fst {

class HierarchyIterator {
public:
	explicit HierarchyIterator(void *&handle) : handle_(handle) {}

	using UnionHolder = pair<vector<uint64_t>, vector<string>>;

	UnionHolder Next() {
		UnionHolder u;
		auto& [ints, strings] = u;
		if (handle_ == nullptr) {
			throw py::stop_iteration();
		}

		auto hier = fstReaderIterateHier(handle_);
		if (hier == nullptr) {
			throw py::stop_iteration();
		}
		ints.push_back(hier->htyp);
		switch (hier->htyp) {
			case FST_HT_SCOPE: {
				auto &scope = hier->u.scope;
				ints.push_back(scope.typ);
				strings.emplace_back(scope.name, scope.name_length);
				strings.emplace_back(scope.component, scope.component_length);
				break;
			}
			case FST_HT_UPSCOPE: {
				break;
			}
			case FST_HT_VAR: {
				auto &var = hier->u.var;
				ints.push_back(var.typ);
				ints.push_back(var.direction);
				ints.push_back(var.handle);
				ints.push_back(var.length);
				ints.push_back(var.is_alias);
				strings.emplace_back(var.name, var.name_length);
				break;
			}
			default: {
				ints.pop_back();
				break;
			}
		}
		return u;
	}

private:
	void *&handle_;
};

class Handler {
public:
	explicit Handler() = default;
	explicit Handler(const string &filename) { Open(filename); }

	~Handler() { Close(); }

	HierarchyIterator CreateHierarchyIterator() {
		return HierarchyIterator(handle_);
	}

	void Open(const string &filename) {
		Close();
		handle_ = fstReaderOpen(filename.c_str());
	}

	void Close() {
		if (handle_ != nullptr) {
			fstReaderClose(handle_);
			handle_ = nullptr;
		}
	}

private:
	void *handle_ = nullptr;
};

} // namespace fst


PYBIND11_MODULE(c_api, m) {
	using namespace fst;
	py::class_<Handler>(m, "HandleClass")
		.def(py::init<>())
		.def(py::init<const std::string &>())
		.def("Open", &Handler::Open)
		.def("Close", &Handler::Close)
		.def("CreateHierarchyIterator", &Handler::CreateHierarchyIterator);

	py::class_<HierarchyIterator>(m, "HierarchyIterator")
		.def(
			"__iter__",
			[](HierarchyIterator &self) -> HierarchyIterator & { return self; }
		)
		.def("__next__", &HierarchyIterator::Next);
}
