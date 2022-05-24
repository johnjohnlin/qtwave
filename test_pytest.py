from main import QtWave
from PySide6 import QtCore, QtGui, QtWidgets
import sys

# happy test with example fst file as opened waveform
def test_with_example():
	FILENAME = "waveform/test_ahb_example.fst"
	app = QtWidgets.QApplication(sys.argv)
	qtwave = QtWave()
	qtwave.module_widget.loadFile(FILENAME)
	qtwave.show()
	app.exec()
