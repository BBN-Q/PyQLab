# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 14:36:22 2012

Model, Viewer and Controller for the LabBrick microwave generators

@author: Colm Ryan
"""

#Path to the dll file
#I don't know why this isn't installed in a standard location
dllPath = 'C:\Qlab software\common\src\+deviceDrivers\@Labbrick\\'

import ctypes
import sys
import timer

from PyQt4 import QtGui, QtCore

#Model for the LabBrick
class LabBrick(object):
    #Constructor
    def __init__(self, serialNum=None):
        #Load the dll (we use cdll becuase the header specifies:
        ##define VNX_FSYNSTH_API __declspec(dllimport)
        self.dll = ctypes.cdll.LoadLibrary(dllPath+'vnx_fmsynth.dll')
        
        #Set to non-test mode
        self.dll.fnLMS_SetTestMode(0)
        
        #See what we have connected
        self.enumerate()
        
        #Connect if a device is specified
        if serialNum is not None:        
            self.connect(serialNum)
        #Otherwise initialize device properties to None
        else:
            self.serialNum = None
            self.devID = None            
            self.maxPower = None
            self.minPower = None
            self.maxFreq = None
            self.minFreq = None
    
    #Destructor to make sure we don't leave the connection open
    def __del__(self):
        self.disconnect()

    def enumerate(self):
        '''
        Helper function to get a list of connected LabBricks device IDs and series numbers.
        '''
        numDevices = self.dll.fnLMS_GetNumDevices()
        
        devIDsArray = numDevices*ctypes.c_uint
        devIDs = devIDsArray()
        self.dll.fnLMS_GetDevInfo(ctypes.byref(devIDs))
        
        self.serialNums = []
        self.devIDs = {}
        for tmpID in devIDs:
            tmpNum = self.dll.fnLMS_GetSerialNumber(tmpID)
            self.serialNums.append(tmpNum)
            self.devIDs[tmpNum] = tmpID
            
    def connect(self, serialNum):
        '''
        Connect and load some basic properties of a LabBrick.
        '''
        #Update the connected devices
        #Hacked out for API bug where opened devices mess things up
#        self.enumerate()
                
        #Error check for a valid serial number
        assert serialNum in self.serialNums , 'Oops! Labbrick {0} is not connected.'.format(serialNum)
        
        #Connect to the device
        status = self.dll.fnLMS_InitDevice(self.devIDs[serialNum])
        assert status == 0 , 'Unable to connect to Labbrick {0}.'.format(serialNum)
        
        #Store the particular deviceID
        self.devID = self.devIDs[serialNum] 
        self.serialNum = serialNum
        
        #Load some specifics about what we connected to
        self.maxPower = self.dll.fnLMS_GetMaxPwr(self.devID)/4
        self.minPower = self.dll.fnLMS_GetMinPwr(self.devID)/4
        self.maxFreq = self.dll.fnLMS_GetMaxFreq(self.devID)/1e8
        self.minFreq = self.dll.fnLMS_GetMinFreq(self.devID)/1e8
        
    def disconnect(self):
        #Close device if open
        if self.open:
            self.dll.fnLMS_CloseDevice(self.devID)
            self.devID = None
            self.serialNum = None

    #Use the status bits to determine if device is open
    #There seems to be two possibilities which I don't understand the difference between
    #define DEV_CONNECTED		0x00000001		// LSB is set if a device is connected
    #define DEV_OPENED	          0x00000002		// set if the device is opened      
    @property
    def open(self):
        if self.devID is not None:
            statusBits = self.dll.fnLMS_GetDeviceStatus(self.devID)
            if statusBits < 2:
                return False
            else:
                return bin(statusBits)[-2] == '1'
        else:
            return False
            
    #Some properties of the device
    def get_frequency(self):
        if self.devID is not None:
            return self.dll.fnLMS_GetFrequency(self.devID)/1e8
        else:
            return None
            
    def set_frequency(self, freq):
        if self.devID is not None:
            assert (freq <= self.maxFreq) and (freq >= self.minFreq), 'Oops! The frequency asked for is outside of the LabBricks range: {0} to {1}.'.format(self.minFreq, self.maxFreq)
            self.dll.fnLMS_SetFrequency(self.devID, int(freq*1e8))
                
    frequency = property(get_frequency, set_frequency)  
    
    def get_power(self):
        if self.devID is not None:
            return self.maxPower - self.dll.fnLMS_GetPowerLevel(self.devID)*0.25
        else:
            return None
        
    def set_power(self, power):
        if self.devID is not None:
            assert(power <= self.maxPower) and (power >= self.minPower), 'Oops! The power asked for is outside of the LabBricks range: {0} to {1}.'.format(self.minPower, self.maxPower)
            self.dll.fnLMS_SetPowerLevel(self.devID, int(power*4))
    
    power = property(get_power, set_power)
    
    def get_freqRef(self):
        if self.devID is not None:
            return self.dll.fnLMS_GetUseInternalRef(self.devID)
        else:
            return None
        
    def set_freqRef(self, freqRef):
        str2boolMap = {'int':True, 'internal':True, 'ext':False, 'external':False}
        if self.devID is not None:
            try:
                self.dll.fnLMS_SetUseInternalRef(self.devID, str2boolMap[freqRef])
            except KeyError:
                self.dll.fnLMS_SetUseInternalRef(self.devID, freqRef)            
        
    freqRef = property(get_freqRef, set_freqRef)
    
    def get_output(self):
        if self.devID is not None:
            return self.dll.fnLMS_GetRF_On(self.devID)
        else:
            return None
    
    def set_output(self, value):
        if self.devID is not None:
            self.dll.fnLMS_SetRFOn(self.devID, value)
            
    output = property(get_output, set_output)
        
    def get_extPulseMod(self):
        if self.devID is not None:
            return self.dll.fnLMS_GetUseInternalPulseMod(self.devID) == 0
        else:
            return None
    
    def set_extPulseMod(self, value):
        if self.devID is not None:
            self.dll.fnLMS_SetUseExternalPulseMod(self.devID, value)
    
    extPulseMod = property(get_extPulseMod, set_extPulseMod)
    
    @property
    def PLLLocked(self):
        if self.devID is not None:
            statusBits = self.dll.fnLMS_GetDeviceStatus(self.devID)
            if statusBits < 64:
                return False
            else:
                return bin(statusBits)[-7] == '1'
        else:
            return None

#QWidget View for the Labbrick
class LabBrickWidget(QtGui.QWidget):
    def __init__(self, labBrick=None):
        super(LabBrickWidget, self).__init__()
        
        self.labBrick = labBrick
        
        self.freqSpinBox = QtGui.QDoubleSpinBox()
        self.freqSpinBox.setRange(self.labBrick.minFreq, self.labBrick.maxFreq)
        self.freqSpinBox.setSuffix('GHz')
        self.freqSpinBox.setDecimals(7)
        self.freqSpinBox.setValue(self.labBrick.frequency)
        self.freqSpinBox.valueChanged.connect(self.labBrick.set_frequency)

        hboxFreq = QtGui.QHBoxLayout()
        hboxFreq.addStretch(1)
        hboxFreq.addWidget(QtGui.QLabel('Frequency:'))
        hboxFreq.addWidget(self.freqSpinBox)
        
        hboxFreqRes = QtGui.QHBoxLayout()
        hboxFreqRes.addStretch(1)
        hboxFreqRes.addWidget(QtGui.QLabel('Freq. Resolution'))
        self.freqResComboBox = QtGui.QComboBox()
        self.freqResComboBox.addItems(['100Hz','1kHz','10kHz','100kHz','1MHz','10MHz','100MHz','1GHz'])
        self.freqResComboBox.setCurrentIndex(7)
        self.freqResComboBox.currentIndexChanged.connect(lambda value: self.freqSpinBox.setSingleStep(10.0**(-7+value)))
        hboxFreqRes.addWidget(self.freqResComboBox)
        
        self.pulseModeCheckBox = QtGui.QCheckBox('External Pulse Mode')
        if self.labBrick.extPulseMod:
            self.pulseModeCheckBox.toggle()
        self.pulseModeCheckBox.stateChanged.connect(self.labBrick.set_extPulseMod)
        
        self.extRefCheckBox = QtGui.QCheckBox('External Freq. Ref.')
        if not self.labBrick.freqRef:
            self.extRefCheckBox.toggle()
        self.extRefCheckBox.stateChanged.connect(lambda value: self.labBrick.set_freqRef(not value))
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(20)
        
        self.RFCheckBox = QtGui.QCheckBox('RF Power On')
        if self.labBrick.output:
            self.RFCheckBox.toggle()
        self.RFCheckBox.stateChanged.connect(self.labBrick.set_output)
        

        self.PLLStatusLabel = QtGui.QLabel()
        #Create a timer to update the PLL status
        self.ctimer = QtCore.QTimer()
        self.ctimer.timeout.connect(self.updatePLLStatus)
                
        grid.addWidget(self.RFCheckBox,0,0)
        grid.addWidget(self.pulseModeCheckBox,1,0)
        grid.addWidget(self.extRefCheckBox,2,0)
        grid.addLayout(hboxFreq,0,1)
        grid.addLayout(hboxFreqRes,1,1)
        grid.addWidget(self.PLLStatusLabel, 2,1)
                
        self.setGeometry(100,100,300,300)
        self.setWindowTitle('Labbrick {0}'.format(self.labBrick.serialNum))
        self.setLayout(grid)
        
        self.ctimer.start(1000)
        
    def updatePLLStatus(self):
        curStatus = self.labBrick.PLLLocked
        if curStatus is None:
            self.PLLStatusLabel.setText('Not Connected')
            self.PLLStatusLabel.setStyleSheet('QLabel {color:black}')
        else:
            if curStatus:
                self.PLLStatusLabel.setText('Locked')
                self.PLLStatusLabel.setStyleSheet('QLabel {color:green}')
            else:
                self.PLLStatusLabel.setText('UnLocked')
                self.PLLStatusLabel.setStyleSheet('QLabel {color:red}')


if __name__ == '__main__':
    print('Got here')
    labBrick = LabBrick(1690)

#    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))
#    QtGui.QApplication.setPalette(QtGui.QApplication.style().standardPalette())

    app = QtGui.QApplication(sys.argv)
    tmpFont = QtGui.QFont()
    tmpFont.setPointSize(12)
    app.setFont(tmpFont)
    labBrickGUI = LabBrickWidget(labBrick)
    labBrickGUI.show()
    
    sys.exit(app.exec_())

    
    