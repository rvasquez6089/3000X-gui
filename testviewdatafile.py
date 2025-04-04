import datetime
import pyqtgraph as pg
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPen

from capturegui import ScopeMetadata
# pg.setConfigOption('background', 'w')
pg.setConfigOption('enableExperimental', True)
pg.setConfigOption('useOpenGL', True)
pg.setConfigOptions(antialias=True)


data = np.load('test_data.npz', allow_pickle=True)
for items in data:
    print(type(data[items]))

metadata = data['metadata'].item()
savedata = data['savedata']
acqtimes = data['acqtimes']
print(f"metadata: {metadata.idn}")
print(f"savedata: {savedata}")
print(f"acqtimes: {acqtimes}")
date = datetime.datetime.fromtimestamp(acqtimes[0], datetime. UTC)
print(date)
print(data)
default_pen = pg.mkPen(color='w', width=1.2)
app = pg.mkQApp("Plotting Example")
win = QtWidgets.QMainWindow()  # Creating blank pyqt5 window
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')
MainPW = pg.PlotWidget()
win.show()

labelStyle = {'color': '#FFF', 'font-size': '20pt'}
MainPW.setLabel('bottom', 'Time (s)', units='s')
MainPW.setLabel('right', 'Voltage', units='V')
MainPW.getPlotItem().getAxis('right').setTextPen('#FFF')
MainPW.getPlotItem().getAxis('bottom').setTextPen('#000')
MainPW.getPlotItem().getAxis('left').hide()
MainPW.getPlotItem().setTitle(
    f'<div><span style="color: #FFF; font-size: 16pt;">Scope Data</div></span>')
MainPW.getPlotItem().layout.setRowFixedHeight(0, 30)
MainPW.getPlotItem().showGrid(x=True, y=True)
MainPW.getPlotItem().titleLabel.setMaximumHeight(60)
MainPW.getPlotItem().addLegend()

# MainPW.plot([1,2,4,8,16,32], name='Voltage')

curves = []
curves.append(MainPW.getPlotItem())


# ax1 = pg.AxisItem('right')
# ax1.linkToView(MainPW.getPlotItem().viewAxis())
# ax1.setLabel('axis 1', color='#ff0000')


## create a new ViewBox, link the right axis to its coordinate system
p2 = pg.ViewBox()
ax2 = pg.AxisItem('right')
curves[0].layout.addItem(ax2, 2, 4)
curves[0].scene().addItem(p2)
ax2.linkToView(p2)
ax2.setLabel(f'<div><span style="color: #FFF; font-size: 16pt;">CH2</div></span>')
p2.setXLink(curves[0])

## create third ViewBox. 
## this time we need to create a new axis as well.
p3 = pg.ViewBox()
ax3 = pg.AxisItem('right')
curves[0].layout.addItem(ax3, 2, 5)
curves[0].scene().addItem(p3)
ax3.linkToView(p3)
p3.setXLink(curves[0])
ax3.setZValue(-10000)
ax3.setLabel(f'<div><span style="color: #FFF; font-size: 16pt;">CH3</div></span>')

p4 = pg.ViewBox()
ax4 = pg.AxisItem('right')
curves[0].layout.addItem(ax4, 2, 6)
curves[0].scene().addItem(p4)
ax4.linkToView(p4)
p4.setXLink(curves[0])
ax4.setZValue(-10000)
ax4.setLabel(f'<div><span style="color: #FFF; font-size: 16pt;">CH4</div></span>')




def updateViews():
    ## view has resized; update auxiliary views to match
    global curves, p2, p3
    p2.setGeometry(curves[0].vb.sceneBoundingRect())
    p3.setGeometry(curves[0].vb.sceneBoundingRect())
    p4.setGeometry(curves[0].vb.sceneBoundingRect())

    ## need to re-update linked axes since this was called
    ## incorrectly while views had different shapes.
    ## (probably this should be handled in ViewBox.resizeEvent)
    p2.linkedViewChanged(curves[0].vb, p2.XAxis)
    p3.linkedViewChanged(curves[0].vb, p3.XAxis)
    p4.linkedViewChanged(curves[0].vb, p4.XAxis)


p1plotcurve = pg.PlotCurveItem( name='CH1 Voltage', pen='y')
MainPW.addItem(p1plotcurve)
updateViews()
curves[0].vb.sigResized.connect(updateViews)
p2plotcurve = pg.PlotCurveItem( pen='g', name='CH2')
p2.addItem(p2plotcurve)
print(p2)
MainPW.getPlotItem().legend.addItem(p2plotcurve, name='CH2')
p3plotcurve = pg.PlotCurveItem( pen='b', name='CH3')
p3.addItem(p3plotcurve)
MainPW.getPlotItem().legend.addItem(p3plotcurve, name='CH3')
p4plotcurve = pg.PlotCurveItem( pen="pink", name='CH4')
p4.addItem(p4plotcurve)
MainPW.getPlotItem().legend.addItem(p4plotcurve, name='CH4')

# MainPW.addItem(curves[0])
win.setCentralWidget(MainPW)
legend = pg.LegendItem((80,60), offset=(70,20))
# legend.setParentItem(MainPW.getPlotItem())

legend.addItem(curves[0], 'bar')
legend.addItem(p2, 'curve1')
legend.addItem(p3, 'curve2')
legend.addItem(p4, 'scatter')


p1plotcurve.setData(x=savedata[0, 0, :],      y=savedata[1, 0, :])
p2plotcurve.setData(x=savedata[0, 0, :],    y=savedata[2, 0, :])
# p3plotcurve.setData(x=savedata[0, 0, :],    y=savedata[3, 0, :])
# p4plotcurve.setData(x=savedata[0, 0, :],    y=savedata[4, 0, :])

for i, ps in enumerate((MainPW.getPlotItem(), p2)):
    meta = metadata.channels[i]
    print(f"channel: {meta.channel} Vrange : {meta.vrange} offset : {meta.offset} ")
    ps.setYRange((meta.vrange*-1) / 2 + meta.offset, meta.vrange / 2 + meta.offset)



pg.exec()