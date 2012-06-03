# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 21:47:31 2012

Model, Viewer and Controller for the QPC box of microwave generators

@author: Colm Ryan
"""

from DigitalAttenuator import DigitalAttenuator, DASingleChannelView
from LabBrick import LabBrick, LabBrickWidget

import sys
from PyQt4 import QtGui, QtCore

class QPC(object):
    def __init__(self, DAPort=None, serialNums=None):
        #If we aren't given serial number is then try and get them from the dll
        if serialNums is None:
            tmpLabBrick = LabBrick()
            self.serialNums = tmpLabBrick.serialNums
            del tmpLabBrick
        else:
            self.serialNums = serialNums
    
        self.DA = DigitalAttenuator(DAPort)
        #Hack arround broken API which won't ennumerate past open LabBricks
#        self.labBricks = [LabBrick(serialNum) for serialNum in self.serialNums]  
        self.labBricks = [LabBrick() for serialNum in self.serialNums]  
        for serialNum,labBrick in zip(self.serialNums, self.labBricks):
            labBrick.connect(serialNum)

class QPCWidget(QtGui.QWidget):
    def __init__(self, QPC=None):
        super(QPCWidget, self).__init__()
        self.QPC = QPC
        
        self.tabWidget = QtGui.QTabWidget(self)        
        
        #Loop through each QPC box and add a tab for it
        self.tabs = []
        for ct,labBrick in enumerate(self.QPC.labBricks):
            self.tabs.append(QtGui.QWidget())
            vbox = QtGui.QVBoxLayout(self.tabs[-1])
            vbox.addWidget(LabBrickWidget(labBrick))
            hbox = QtGui.QHBoxLayout()
            hbox.addStretch(1)
            hbox.addWidget(QtGui.QLabel('Attenuator:'))
            hbox.addWidget(DASingleChannelView(self.QPC.DA, ct+1))
            vbox.addLayout(hbox)
            self.tabWidget.addTab(self.tabs[-1], str(labBrick.serialNum))
        
        self.setWindowTitle('BBN QPC')
        self.resize(self.tabWidget.sizeHint())
        self.show()
        
if __name__ == '__main__':
    print('Got here')
    app = QtGui.QApplication(sys.argv)
    tmpFont = QtGui.QFont()
    tmpFont.setPointSize(12)
    app.setFont(tmpFont)    
    
    tmpQPC = QPC('COM6')
    qpcWidget = QPCWidget(tmpQPC)
    sys.exit(app.exec_())

        
        
        
        
        
        