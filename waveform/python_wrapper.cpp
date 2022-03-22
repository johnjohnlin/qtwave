#define PY_SSIZE_T_CLEAN
#include "waveform_fst.h"
#include <Python.h>
#include <numpy/ndarrayobject.h>
#include <algorithm>
#include <memory>
#include <vector>
using namespace std;

#ifndef MODULE_NAME
#define MODULE_NAME waveformloader_c
#endif
#define XSTR(s) #s
#define XXCONCAT(a, b) a##_##b
#define XCONCAT(a, b) XXCONCAT(a, b)
#define MODULE_NAME_STR XSTR(MODULE_NAME)
#define MODULE_FUNCNAME(f) XCONCAT(f, MODULE_NAME)

constexpr static int CeilDev(const int a, const int b) {
	return (a+b-1)/b;
}

static PyObject* VectorToPythonTuple(const vector<PyObject*> v) {
	PyObject *tup = PyTuple_New(v.size());
	for (int i = 0; i < v.size(); ++i) {
		PyTuple_SET_ITEM(tup, i, v[i]);
	}
	return tup;
}

static PyObject* VectorToPythonList(const vector<PyObject*> v) {
	PyObject *tup = PyList_New(v.size());
	for (int i = 0; i < v.size(); ++i) {
		PyList_SET_ITEM(tup, i, v[i]);
	}
	return tup;
}

/**
	\brief Create numpy array from C++ vector.

	\param num_samples Number of value change sample.
	\param vector_size vector.size()
	\param vector_type_size sizeof(vector::value_type)
	\param array_typenum vector.data()
	\param none_if_allzero Return Py_None if input is all zero and increase its reference.
*/
static PyObject* CreateLinearNpArray(
	const size_t vector_size,
	const size_t vector_type_size,
	const char *vector_data_ptr,
	bool none_if_allzero
) {
	if (
		none_if_allzero and
		all_of(vector_data_ptr, vector_data_ptr + vector_size*vector_type_size, [](const char t){ return t == 0; } )
	) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	const int value_type = [](const size_t sz) -> int {
		int value_type;
		switch (sz) {
			case 1: { value_type = NPY_UINT8; break; }
			case 2: { value_type = NPY_UINT16; break; }
			case 4: { value_type = NPY_UINT32; break; }
			default: { value_type = NPY_UINT64; break; }
		}
		return value_type;
	}(vector_type_size);
	PyObject *ret = nullptr;
	npy_intp arr_dims = vector_size;
	ret = PyArray_SimpleNew(1, &arr_dims, value_type);
	auto iter = NpyIter_New(
		reinterpret_cast<PyArrayObject*>(ret),
		NPY_ITER_WRITEONLY | NPY_ITER_EXTERNAL_LOOP | NPY_ITER_REFS_OK,
		NPY_KEEPORDER, NPY_NO_CASTING, nullptr
	);
	auto iternext = NpyIter_GetIterNext(iter, nullptr);
	char **dataptr = NpyIter_GetDataPtrArray(iter);
	npy_intp* strideptr = NpyIter_GetInnerStrideArray(iter);
	npy_intp* innersizeptr = NpyIter_GetInnerLoopSizePtr(iter);
	assert(NpyIter_GetDescrArray(iter)[0]->elsize == vector_type_size);
	do {
		char *data = *dataptr;
		npy_intp stride = *strideptr;
		npy_intp count = *innersizeptr;
		if (size_t(stride) == vector_type_size) {
			const npy_intp nbyte = stride * count;
			memcpy(data, vector_data_ptr, nbyte);
			data += nbyte;
			vector_data_ptr += nbyte;
		} else {
			while (count--) {
				*data = *vector_data_ptr;
				data += stride;
				vector_data_ptr += vector_type_size;
			}
		}
	} while (iternext(iter));
	NpyIter_Deallocate(iter);
	return ret;
}

/**
	\brief Create a Python list from C++ hierarchy commands.
*/
static PyObject* HierarchyCommandToPythonList(const vector<HierarchyCommand> &hier_cmd) {
	vector<PyObject*> v(hier_cmd.size());
	transform(
		hier_cmd.begin(), hier_cmd.end(), v.begin(),
		[](const HierarchyCommand& h) -> PyObject* {
			PyObject *hier_type_py = PyLong_FromLong(h.hier_type_);
			PyObject *secondary_type_py = PyLong_FromLong(h.secondary_type_);
			PyObject *signal_idx_py = PyLong_FromLong(h.signal_idx_);
			PyObject *name_py = PyUnicode_FromString(h.name_.c_str());
			return VectorToPythonTuple({
				hier_type_py,
				secondary_type_py,
				signal_idx_py,
				name_py
			});
		}
	);
	return VectorToPythonList(v);
}

/**
	\brief Create a Python dict from C++ signal data structure.
*/
static PyObject* SignalToPythonDict(std::unordered_map<uint64_t, std::unique_ptr<SignalData>> &signals) {
	PyObject *signals_pydict = PyDict_New();
	for (auto &idx_sig: signals) {
		auto &idx = idx_sig.first;
		auto &sig = *idx_sig.second;
		const size_t num_samples = sig.get_num_sample();
		const int nbit = sig.get_nbit();
		const char *timepoint_ptr = reinterpret_cast<char*>(sig.get_timepoint_pointer());
		const char *data01_ptr, *dataxz_ptr;
		sig.get_vector_pointers(data01_ptr, dataxz_ptr);
		const size_t vector_size = sig.get_vector_size();
		const size_t vector_type_size = sig.get_vector_type_size();
		PyObject *timepoint_np = CreateLinearNpArray(num_samples, 8, timepoint_ptr, false);
		PyObject *data01_np = CreateLinearNpArray(vector_size, vector_type_size, data01_ptr, false);
		PyObject *dataxz_np = CreateLinearNpArray(vector_size, vector_type_size, dataxz_ptr, true);
		PyObject *tup = VectorToPythonTuple({
			PyLong_FromLong(nbit),
			PyLong_FromLong(num_samples),
			timepoint_np,
			data01_np,
			dataxz_np
		});
		PyDict_SetItem(signals_pydict, PyLong_FromLong(idx), tup);
		sig.Destroy();
	}
	return signals_pydict;
}

static PyObject* Waveform2Python(Waveform &waveform) {
	PyObject *timescale_py = PyLong_FromLong(waveform.timescale_);
	PyObject *hierarchy_py = HierarchyCommandToPythonList(waveform.hier_cmd_);
	PyObject *signals_pydict = SignalToPythonDict(waveform.signals_);
	return VectorToPythonTuple({
		timescale_py,
		hierarchy_py,
		signals_pydict,
	});
}

static PyObject* MODULE_FUNCNAME(ParseFstWaveform)(PyObject *self, PyObject *args) {
	const char *file_name;
	unique_ptr<Waveform> waveform;
	if (
		not PyArg_ParseTuple(args, "s", &file_name) or
		ParseFst(file_name, waveform) != 0
	) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	return Waveform2Python(*waveform.get());
}

static PyObject* MODULE_FUNCNAME(ParseVcdWaveform)(PyObject *self, PyObject *args) {
	Py_INCREF(Py_None);
	return Py_None;
}

PyMODINIT_FUNC MODULE_FUNCNAME(PyInit)() {
	static PyMethodDef methods[] = {
		{"ParseFstWaveform", MODULE_FUNCNAME(ParseFstWaveform), METH_VARARGS, ""},
		{"ParseVcdWaveform", MODULE_FUNCNAME(ParseVcdWaveform), METH_VARARGS, ""},
		{nullptr, nullptr, 0, nullptr}
	};
	static PyModuleDef moduledef = {
		PyModuleDef_HEAD_INIT,
		MODULE_NAME_STR,
		nullptr, -1,
		methods,
		nullptr, nullptr, nullptr, nullptr
	};
	import_array();
	return PyModule_Create(&moduledef);
}
