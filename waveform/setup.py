#!/usr/bin/env python3
from setuptools import setup, Extension
from numpy import get_include
from glob import glob
from sysconfig import get_config_var
setup(
	name='WaveformLoader',
	version='0.1',
	author='Yu-Sheng Lin',
	author_email='johnjohnlys@gmail.com',
	ext_modules=[
		Extension(
			'waveformloader_c',
			[
				'python_wrapper.cpp',
				'waveform.cpp',
				'waveform_fst.cpp',
				'fastlz.c',
				'fstapi.c',
				'lz4.c',
			],
			define_macros=[
				('NDEBUG', None),
				('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
				('MODULE_NAME', 'waveformloader_c'),
			],
			libraries=['z', "python" + get_config_var('LDVERSION'),],
			extra_compile_args=['--std=c++11'],
			include_dirs=[get_include()],
		),
	]
)
