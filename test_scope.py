import pyqtgraph as pg


import numpy as np
from PyQt5 import QtWidgets

# For future Python3 compatibility:


import os
import random
import time

import pyvisa as visa
import sys
from time import sleep

# Set to the IP address of the oscilloscope
# agilent_msox_3034a = os.environ.get('MSOX3000_IP', 'TCPIP0::172.16.2.13::INSTR')

import argparse

app = pg.mkQApp("Plotting Example")
#mw = QtWidgets.QMainWindow()
#mw.resize(800,800)
pg.setConfigOption('background', 'w')
pg.setConfigOption('enableExperimental', True)
pg.setConfigOption('useOpenGL', True)
# pg.setConfigOption('useCupy', True)
labelStyle = {'color': '#000', 'font-size': '12pt'}
win = QtWidgets.QMainWindow()  # Creating blank pyqt5 window
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')


mainpw = pg.PlotWidget()
win.setCentralWidget(mainpw)
default_pen = pg.mkPen(color='b')

maincurve = pg.PlotCurveItem(pen=default_pen)
mainpw.addItem(maincurve)
mainpw.getPlotItem().showGrid(x=True, y=True)
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)



parser = argparse.ArgumentParser(
    description='Get a screen capture from Agilent/KeySight MSO3034A scope and save it to a file')
parser.add_argument('ofile', nargs=1, help='Output file name')
args = parser.parse_args()

fn_ext = ".png"
pn = "/Downloads"
fn = pn + "/" + args.ofile[0]

while os.path.isfile(fn + fn_ext):
    fn += "-" + random.choice("abcdefghjkmnpqrstuvwxyz")

fn += fn_ext

import msox3000.msox3000.MSOX3000 as MSOX3000

rm = visa.ResourceManager('@py')
resources = rm.list_resources()
print(resources)

## Connect to the Power Supply with default wait time of 100ms
scope = MSOX3000(resources[0])
scope.open()

print(scope.idn())

chan = '1'
# print("Ch.{}: {}V ACRMS".format(chan, scope.measureDVMacrms(chan)))
# print("Ch.{}: {}V DC".format(chan, scope.measureDVMdc(chan)))
# print("Ch.{}: {}V DCRMS".format(chan, scope.measureDVMdcrms(chan)))
# print("Ch.{}: {}Hz FREQ".format(chan, scope.measureDVMfreq(chan)))
#
# print(scope.measureVoltAmplitude('1', install=True))
# print(scope.measureVoltMax('1', install=True))
# print(scope.measureVoltMax(install=False))

# stats = scope.measureStatistics()
mainpw.setLabel('bottom', 'Time (s)', units='s')
mainpw.getPlotItem().getAxis('left').setTextPen('#000')
mainpw.getPlotItem().getAxis('bottom').setTextPen('#000')
win.show()
# scope._instWrite("SINGle")


scope.DEBUG = True
# time.sleep(1)
scope._instWrite("SINGle")
time.sleep(0.1)
data, time = scope.waveform("none", channel='1', points=4000000)
# scope._inst.write("WAVeform:DATA?")# print(stats)
# data = scope._inst.read_bytes(496)
# data = scope._inst.write("WAVeform:DATA?")# print(stats)
print(f"Lenght: {len(data)}")
print(f"data {data}")
maincurve.setData(y=data, x=time)
np.save('test.npy', data)


# print("Ch.{}: {}V ACRMS".format(chan, scope.measureDVMacrms(chan)))
# print("Ch.{}: {}V DC".format(chan, scope.measureDVMdc(chan)))
# print("Ch.{}: {}V DCRMS".format(chan, scope.measureDVMdcrms(chan)))
# print("Ch.{}: {}Hz FREQ".format(chan, scope.measureDVMfreq(chan)))
print('Done')

scope.close()
pg.exec()