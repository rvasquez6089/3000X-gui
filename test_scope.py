import pyqtgraph as pg


import numpy as np
from PyQt5 import QtWidgets, QtCore

# For future Python3 compatibility:


import os
import random
import time

import pyvisa as visa
from pyvisa.highlevel import list_backends
import sys
from time import sleep

# Set to the IP address of the oscilloscope
# agilent_msox_3034a = os.environ.get('MSOX3000_IP', 'TCPIP0::172.16.2.13::INSTR')

import argparse

from quantiphy import Quantity

app = pg.mkQApp("Plotting Example")
#mw = QtWidgets.QMainWindow()
#mw.resize(800,800)
pg.setConfigOption('background', 'w')
pg.setConfigOption('enableExperimental', True)
pg.setConfigOption('useOpenGL', True)
pg.setConfigOptions(antialias=True)
# pg.setConfigOption('useCupy', True)
labelStyle = {'color': '#000', 'font-size': '12pt'}
win = QtWidgets.QMainWindow()  # Creating blank pyqt5 window
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')


mainpw = pg.PlotWidget()
win.setCentralWidget(mainpw)
default_pen = pg.mkPen(color='b', width=1.2)

maincurve = pg.PlotCurveItem(pen=default_pen)
secondcurve= pg.PlotCurveItem(pen=default_pen)
mainpw.addItem(maincurve)
mainpw.addItem(secondcurve)
mainpw.getPlotItem().showGrid(x=True, y=True)
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)








import msox3000.msox3000.MSOX3000 as MSOX3000

# rm = visa.ResourceManager("")
print(list_backends())
rm = visa.ResourceManager("@ivi")

resources = rm.list_resources()
print(resources)

## Connect to the Power Supply with default wait time of 100ms
scope = MSOX3000((resources[0], rm))
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
# scope._instWrite("SINGle")
# time.sleep(0.1)
data, timearr = scope.waveform("none", channel='3')
# data2, time = scope.waveform("none", channel='2', points=100000)

# scope._inst.write("WAVeform:DATA?")# print(stats)
# data = scope._inst.read_bytes(496)
# data = scope._inst.write("WAVeform:DATA?")# print(stats)
print(f"Length: {len(data)}")
print(f"data {data}")
maincurve.setData(y=data, x=timearr)
# secondcurve.setData(y=data2, x=time)
np.save('test.npy', data)
last = time.perf_counter()
for channel in range(1, 5):
    if scope.get_channel_displayed(channel):
        start = time.perf_counter()
        units = (scope.get_channel_units(channel))
        print(f"Channel {channel} get_channel_units: {units}")
        # print(f"Channel: {channel} Displayed: {scope.get_channel_displayed(channel)}")
        print(f"Channel {channel} BW: {scope.get_channel_bw(channel)}")
        print(
            f"Channel {channel} channel BW limit: {scope.get_channel_bw_limit(channel)}")
        print(
            f"Channel {channel} get_channel_coupling: {scope.get_channel_coupling(channel)}")
        print(
            f"Channel {channel} get_channel_offset: {scope.get_channel_offset(channel, units)}")
        print(
            f"Channel {channel} get_channel_impedance: {(scope.get_channel_impedance(channel))}")
        print(f"Channel {channel} get_channel_inverted: {scope.get_channel_inverted(channel)}")
        print(
            f"Channel {channel} get_channel_label: {scope.get_channel_label(channel)}")
        print(
            f"Channel {channel} get_channel_offset: {scope.get_channel_offset(channel, units)}")
        print(
            f"Channel {channel} get_channel_probe_factor: {scope.get_channel_probe_factor(channel)}")
        print(
            f"Channel {channel} get_channel_skew: {(scope.get_channel_skew(channel))}")
        print(f"Channel {channel} get_channel_range: {scope.get_channel_range(channel, units)}")
        print(
            f"Channel {channel} get_channel_scale: {scope.get_channel_scale(channel, units)}")

        print(f"Channel {channel} get_channel_vernier: {scope.get_channel_vernier(channel)}")
        print(f"Time to get channel settings {Quantity(time.perf_counter() - start, 's')}")
# def update():
#     global scope, maincurve, last
#     scope._instWrite("SINGle")
#     waveform_data = np.frombuffer((scope._instQueryIEEEBlock("WAVeform:DATA?", chunk_size=100100)), dtype=np.uint8)
#     timearr = ((np.arange(len(waveform_data))))
#     maincurve.setData(y=waveform_data, x=timearr)
#     print(f"time {time.perf_counter() - last}")
#     last = time.perf_counter()


# print("Ch.{}: {}V ACRMS".format(chan, scope.measureDVMacrms(chan)))
# print("Ch.{}: {}V DC".format(chan, scope.measureDVMdc(chan)))
# print("Ch.{}: {}V DCRMS".format(chan, scope.measureDVMdcrms(chan)))
# print("Ch.{}: {}Hz FREQ".format(chan, scope.measureDVMfreq(chan)))
# print('Done')
# timer = QtCore.QTimer()
# timer.timeout.connect(update)
# timer.start(10)

# scope.close()
pg.exec()