'''
Created on Jan 8, 2012

@author: cryan

A simple GUI for plotting pulse sequences for visual inspection
'''

AWGFreq = 1e9


import sys

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

from PySide import QtCore, QtGui

import numpy as np

import PulseSequencer

class PulseSeqPlotWindow(QtGui.QWidget):
    
    def __init__(self, AWGWFs=None):
        super(PulseSeqPlotWindow, self).__init__()
        
        self.AWGWFs = AWGWFs
        
        if AWGWFs.keys()[0][:6] == 'TekAWG':
            numSeqs = len(AWGWFs.values()[0].values()[0])
        elif AWGWFs.keys()[0][:6] == 'BBNAPS':
            numSeqs = len(AWGWFs[AWGWFs.keys()[0]]['ch1']['LLs'])
        else:
            raise NameError('Unknown AWG Type: we currently only handle TekAWG and BBNAPS.')
            
        #Convert the BBNAPS LLs into pulse sequence waveforms
        for tmpAWGName, tmpAWG in AWGWFs.items():
            if tmpAWGName[:6] == 'BBNAPS':
                tmpWFs = {}
                for chanStr in tmpAWG.keys():
                    tmpWFs[chanStr] = []
                    for miniLL in tmpAWG[chanStr]['LLs']:
                        tmpWFs[chanStr].append(PulseSequencer.LL2sequence(miniLL, tmpAWG[chanStr]['WFLibrary']))
                AWGWFs[tmpAWGName] = tmpWFs
                        
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
        slider.setRange(0, numSeqs-1)
        slider.setTickInterval(1)
        slider.setSingleStep(1)
        sliderLabel = QtGui.QLabel('Sequence Num.')
        if numSeqs > 1:
            numDigits = int(np.ceil(np.log10(numSeqs-1)))
        else:
            numDigits = 1
        sliderLCD = QtGui.QLCDNumber(numDigits)
        slider.valueChanged.connect(sliderLCD.display)
        slider.valueChanged.connect(self.update_plot)
        self.slider = slider
        
        #A tree view to decide what to plot
        plotCheckBoxes = QtGui.QTreeWidget()
        plotCheckBoxes.setMinimumWidth(150)
        plotCheckBoxes.setHeaderLabel('Channel Plot')
        plotCheckBoxes.itemClicked.connect(self.update_plot)
        for tmpAWGName, tmpAWG in AWGWFs.items():
            tmpItem = QtGui.QTreeWidgetItem([tmpAWGName])
            for tmpChannelName in sorted(tmpAWG.keys()):
                tmpChildItem = QtGui.QTreeWidgetItem([tmpChannelName])
                tmpChildItem.setCheckState(0,QtCore.Qt.Checked)
                tmpItem.addChild(tmpChildItem)
            plotCheckBoxes.addTopLevelItem(tmpItem)
            tmpItem.setExpanded(True)
        self.plotCheckBoxes = plotCheckBoxes
        
        
        delayShiftCheckBox = QtGui.QCheckBox('Undo Delays')
        delayShiftCheckBox.stateChanged.connect(self.update_plot)
        delayShiftCheckBox.setEnabled(False)
        
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
                    self.ax.plot(self.AWGWFs[tmpAWGName][str(tmpChild.text(0))][curSegNum] + vertShift)
                    self.ax.text(0, vertShift,tmpAWGName+'-'+str(tmpChild.text(0)), fontsize=8)
                    vertShift += 2
        self.ax.set_ylim((-1, vertShift))                    
        self.canvas.draw()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())         
        

def plot_pulse_seqs(AWGWFs):
    
    #Look to see if iPython's event loop is running
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)

    plotterWindow = PulseSeqPlotWindow(AWGWFs)
    plotterWindow.show()

    try: 
        from IPython.lib.guisupport import start_event_loop_qt4
        start_event_loop_qt4(app)
    except ImportError:
        sys.exit(app.exec_())
       
    #Need to a keep a reference to the window alive.
    return plotterWindow


if __name__ == '__main__':
    
    AWGWFs = {}
    AWGWFs['TekAWG1'] = {}
    AWGWFs['TekAWG1']['ch1'] = []
    AWGWFs['TekAWG1']['ch2'] = []
    AWGWFs['TekAWG1']['ch1m1'] = []
    
    for ct in range(1,10):
        AWGWFs['TekAWG1']['ch1'].append(np.sin(np.linspace(0,ct*np.pi,10000)))
        AWGWFs['TekAWG1']['ch2'].append(np.cos(np.linspace(0,ct*np.pi,10000)))
        AWGWFs['TekAWG1']['ch1m1'].append(np.abs(AWGWFs['TekAWG1']['ch1'][-1]) < 0.5)
    
    
    plot_pulse_seqs(AWGWFs)