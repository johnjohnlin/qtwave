#!/usr/bin/env bash
cd qtwave_
python -m unittest discover -s . -p "*_test.py" -t ..
