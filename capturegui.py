import os
import sys
import time
import uuid
from enum import Enum

import numpy as np
import pyvisa
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.uic.properties import QtGui
from quantiphy.quantiphy import Quantity

from msox3000.msox3000 import MSOX3000
from scopemetadata import ScopeMetadata
from ui_capturegui import Ui_MainWindow
import pyqtgraph as pg

settings_path = None



class PersistentGUISettings:
    def __init__(self):
        if os.name == 'nt':
            self.settings_path = os.getenv('APPDATA')
        else:
            self.settings_path = None
        self.acquisitions = 1
        self.points = 10000
        self.save_path = None
        self.filename = 'Test'
        self.overwrite = False



class GenericThread(QThread):
    def __init__(self, func: callable):
        super().__init__()
        self.func = func

    @pyqtSlot()
    def run(self):
        try:
            self.func()
        except Exception as e:
            print(e)



class CaptureGui(QMainWindow):
    def __init__(self):
        default_pen = pg.mkPen(color='b', width=2)
        super(CaptureGui, self).__init__()
        self.loadsettings()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scope: MSOX3000

        labelStyle = {'color': '#000', 'font-size': '12pt'}
        self.ui.MainPW.setLabel('bottom', 'Time (s)', units='s')
        self.ui.MainPW.setLabel('left', 'Voltage (V)', units='V')
        self.ui.MainPW.getPlotItem().getAxis('left').setTextPen('#000')
        self.ui.MainPW.getPlotItem().getAxis('bottom').setTextPen('#000')
        self.ui.MainPW.getPlotItem().setTitle(
            f'<div><span style="color: #000; font-size: 16pt;">Scope Data</div></span>')
        self.ui.MainPW.getPlotItem().layout.setRowFixedHeight(0, 30)
        self.ui.MainPW.getPlotItem().showGrid(x=True, y=True)
        self.ui.MainPW.getPlotItem().titleLabel.setMaximumHeight(60)

        self.maincurve = pg.PlotCurveItem(pen=default_pen)
        self.ui.MainPW.addItem(self.maincurve)
        # self.ui.MainPW.removeItem(self.maincurve)
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        for resource in resources:
            self.ui.scopelistcombox.addItem(resource)

    def loadsettings(self):
        if os.name == 'nt':
            settings_path = os.getenv('APPDATA')
        else:
            settings_path = os.getcwd()
        filepath = settings_path+ '.3000xgui_settings.rtv3000'
        if os.path.exists(filepath):
            np.load(filepath)
        else:
            settings = PersistentGUISettings()
            np.savez(filepath, settings)




    @pyqtSlot()
    def on_ConnectButton_clicked(self):
        import msox3000.msox3000.MSOX3000 as MSOX3000

        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        print(resources)

        ## Connect to the Power Supply with default wait time of 100ms
        self.scope = MSOX3000((resources[0], rm))
        self.scope.open()

        self.ui.InfoText.append(f"Connected to {resources[0]}")
        self.ui.InfoText.append(f"Device: {self.scope.idn()}")

    @pyqtSlot()
    def on_AcqDataButton_clicked(self):
        self.collect_thread = GenericThread(self.collect_data)
        self.collect_thread.start()


    def collect_data(self):

        metadata = ScopeMetadata()
        metadata.get_metadata(self.scope)
        self.scope._instWrite(f"WAVeform:SOURce CHAN{metadata.channels[0].channel}")
        preamble = self.scope.read_preamble()
        print(f"points available: {self.scope.get_acquired_points()}")

        points = min(self.scope.get_acquired_points(), int(self.ui.userdatapointsle.text()))
        self.scope.set_waveform_points(points)
        preamble = self.scope.read_preamble()
        savedata = np.zeros((len(metadata.channels)+1, int(self.ui.acquisitionnumberle.text()), preamble.wfmpts), dtype=np.float32)
        self.ui.userdatapointsle.setText(str(preamble.wfmpts))
        acqtimes = np.zeros(int(self.ui.acquisitionnumberle.text()))

        for i in range(int(self.ui.acquisitionnumberle.text())):
            if self.ui.SingleRetriggerChBox.isChecked():
                self.scope.single_acquire()
                self.scope._instQuery("*OPC?")
                time.sleep(0.1)
            if self.ui.ScreenshotChBox.isChecked():
                self.scope.hardcopy('test.png')
            acqtimes[i] = time.time()
            for j in range(len(metadata.channels)):
                start = time.time()
                print(f"{i} {j} Getting data channel {metadata.channels[j].channel}")
                data, timearr = self.scope.waveform("none", channel=metadata.channels[j].channel)
                print(f"Time to transfer data = {time.time() - start}")
                self.maincurve.setData(y=data, x=timearr)
                self.ui.MainPW.autoRange()
                savedata[0, i, :] = timearr
                savedata[j+1, i, :] = data


        np.savez('test_data.npz', metadata=metadata, savedata=savedata, acqtimes=acqtimes, allow_pickle=True)
        print(metadata.idn)
        print(f"Length: {len(data)}")
        print(f"data {data}")

    @pyqtSlot()
    def on_selectsavepathbut_clicked(self):
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        self.ui.savepathlabel.setText(folder_path)


    def plot_data_on_live_plot(self, metadata: ScopeMetadata, data):
        pass



if __name__ == "__main__":
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('enableExperimental', True)
    pg.setConfigOption('useOpenGL', True)
    pg.setConfigOptions(antialias=False)
    app = QApplication(sys.argv)
    window = CaptureGui()
    window.show()
    app.exec_()
