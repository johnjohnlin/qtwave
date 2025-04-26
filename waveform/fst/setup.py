from setuptools import setup, Extension
import pybind11

ext_modules = [
	Extension(
		"c_api",
		["c_api.cpp", "fstapi.c", "lz4.c", "fastlz.c"],
		include_dirs=[pybind11.get_include()],
		libraries=["z"],
		language="c++",
		extra_compile_args=["-std=c++17"],
	),
]

setup(
	name="c_api",
	version="1.0",
	ext_modules=ext_modules,
)
