'''
Created on Jan 8, 2012

@author: cryan

A simple GUI for plotting pulse sequences for visual inspection
'''

AWGFreq = 1e9

import numpy as np

import sys
import os
import matplotlib
matplotlib.use('Qt4Agg')
#matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

from PyQt4 import QtCore, QtGui


class PulseSeqPlotWindow(QtGui.QWidget):
    
    def __init__(self, AWGWFs=None):
        super(PulseSeqPlotWindow, self).__init__()
        
        self.AWGWFs = AWGWFs
        
        #Count up total number of channels
        numSeqs = 0
        for tmpAWG in AWGWFs[0].values():
            numSeqs += len(tmpAWG)
        
        #Create the GUI
        self.resize(1000,700)
        self.center()
        self.setWindowTitle('Pulse Sequence Plotter')
        
        
        # generate the plot
        self.fig = Figure(figsize=(12,6), dpi=72)
        self.ax = self.fig.add_subplot(111)

        # generate the canvas to display the plot
        self.canvas = FigureCanvas(self.fig)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        
        #Create a slider to move through the different sequences
        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, len(self.AWGWFs)-1)
        slider.setTickInterval(1)
        slider.setSingleStep(1)
        sliderLabel = QtGui.QLabel('Sequence Num.')
        sliderLCD = QtGui.QLCDNumber(int(np.ceil(np.log10(len(self.AWGWFs)-1))))
        slider.valueChanged.connect(sliderLCD.display)
        slider.valueChanged.connect(self.update_plot)
        self.slider = slider
        
        #A tree view to decide what to plot
        plotCheckBoxes = QtGui.QTreeWidget()
        plotCheckBoxes.setMinimumWidth(150)
        plotCheckBoxes.setHeaderLabel('Channel Plot')
        plotCheckBoxes.itemClicked.connect(self.update_plot)
        for tmpAWGName, tmpAWG in AWGWFs[0].iteritems():
            tmpItem = QtGui.QTreeWidgetItem([tmpAWGName])
            for tmpChannelName in tmpAWG.keys():
                tmpChildItem = QtGui.QTreeWidgetItem([tmpChannelName])
                tmpChildItem.setCheckState(0,QtCore.Qt.Checked)
                tmpItem.addChild(tmpChildItem)
            plotCheckBoxes.addTopLevelItem(tmpItem)
            tmpItem.setExpanded(True)
        self.plotCheckBoxes = plotCheckBoxes
        
        delayShiftCheckBox = QtGui.QCheckBox('Undo Delays')
        delayShiftCheckBox.stateChanged.connect(self.update_plot)
        
        #Lay everything out
        hboxSlider = QtGui.QHBoxLayout()
        hboxSlider.addStretch(1)
        hboxSlider.addWidget(sliderLabel)
        hboxSlider.addWidget(sliderLCD)
        hboxSlider.addWidget(slider)

        vboxOptions = QtGui.QVBoxLayout()
        vboxOptions.addWidget(plotCheckBoxes)
        vboxOptions.addWidget(delayShiftCheckBox)
        vboxOptions.addStretch(1)

        hboxTop = QtGui.QHBoxLayout()
        hboxTop.addWidget(self.canvas)
        hboxTop.addLayout(vboxOptions)
        
        hboxBottom = QtGui.QHBoxLayout()
        hboxBottom.addWidget(self.mpl_toolbar)
        hboxBottom.addStretch(1)
        hboxBottom.addLayout(hboxSlider)
        
        vboxTot = QtGui.QVBoxLayout()
        vboxTot.addLayout(hboxTop)
        vboxTot.addLayout(hboxBottom)
        
        self.setLayout(vboxTot) 
        
        self.update_plot()
        
    def update_plot(self):
        
        self.ax.clear()

        #Get the current segment number
        curSegNum = self.slider.sliderPosition()
        
        vertShift = 0
        for itemct in range(self.plotCheckBoxes.topLevelItemCount()):
            tmpItem = self.plotCheckBoxes.topLevelItem(itemct)
            tmpAWGName = str(tmpItem.text(0))
            for childct in range(tmpItem.childCount()):
                tmpChild = tmpItem.child(childct)
                if tmpChild.checkState(0) == QtCore.Qt.Checked:
                    self.ax.plot(self.AWGWFs[curSegNum][tmpAWGName][str(tmpChild.text(0))] + vertShift)
                    vertShift += 2
                    
        self.canvas.draw()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())         
        

def plot_pulse_seq(pulseSeq=None):
    pass
    

if __name__ == '__main__':
    
    AWGWFs = []
    for ct in range(1,10):
        tmpWFs = {}
        tmpWFs['Tek1'] = {}
        tmpWFs['Tek1']['ch1'] = np.sin(np.linspace(0,ct*np.pi,10000))
        tmpWFs['Tek1']['ch2'] = np.cos(np.linspace(0,ct*np.pi,10000))
        tmpWFs['Tek1']['ch1m1'] = np.abs(tmpWFs['Tek1']['ch1']) < 0.5
        AWGWFs.append(tmpWFs)
    
    app = QtGui.QApplication(sys.argv)

    plotterWindow = PulseSeqPlotWindow(AWGWFs)
    plotterWindow.show()



    sys.exit(app.exec_())

    
#    plot_pulse_seq(AWGWFs)