# PoC
```
cd waveform
python setup.py build_ext --inplace
python
>>> import waveformloader
>>> x = waveformloader.ParseFstWaveform("test_ahb_example.fst")
>>> print(x)
```
