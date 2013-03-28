# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 15:20:39 2012

Model, Viewer and Controller for the Arduino controlled microwave 
digital attenuator card.
@author: Colm Ryan
"""

#We use the PySerial module to communicate via a USB serial emmulator
import serial

import sys
import time
from PySide import QtGui, QtCore

#Model for the card
class DigitalAttenuator(object):
    #Constructor
    def __init__(self, port=None):
        
        if port is not None:
            self.connect(port)
        else:
            self.socket=None

        #Some properties
        self.maxAttenuation = 31.5
        self.minAttenuation = 0
        self.maxChannels = 3

    def __del__(self):
        if self.socket is not None:
            self.disconnect()
        
    def connect(self, port):
        #Connect at a faster baudrate?  115200 seems to flake out.
        self.socket = serial.Serial(port, timeout=0.1, baudrate=115200)
        #Have to sleep here or else the socket flakes out if we send commands too quicly
        time.sleep(2)
        
    def disconnect(self):
        if self.socket.isOpen():
            self.socket.close()
    
    #The Arduino sends line data and then finished with a 'END\r\n' line
    def read(self):
        assert self.socket.isOpen() , 'Oops! Tried to read from closed DigitalAttenuator.'
        output = []
        tmpLine = self.socket.readline()
        if tmpLine == '':
            print('Dead line.')
            return None
        while (tmpLine[:3] != 'END'):
            output.append(tmpLine)
            tmpLine = self.socket.readline()
            #Check for timeout
            if tmpLine == '':
                break
        return output

    def write(self, writeStr):
        assert self.socket.isOpen() , 'Oops! Tried to write to closed DigitalAttenuator.'
        self.socket.write(writeStr)

    def query(self, queryStr):
        self.write(queryStr)
        #Seems to need a pause on faster systems
        time.sleep(0.01)
        return self.read()
        
        
    def getAttenuation(self, channel):
        assert (channel>=1) and (channel<=self.maxChannels), 'Oops the Digital Attenuator has only {0} channels.'.format(self.maxChannels)
        return float(self.query('GET {0} '.format(int(channel)))[0])
    
    def setAttenuation(self, channel, attenuation):
        assert (channel>=1) and (channel<=self.maxChannels), 'Oops the Digital Attenuator has only {0} channels.'.format(self.maxChannels)
        assert (attenuation <= self.maxAttenuation) and (attenuation >= self.minAttenuation)
        self.write('SET {0} {1:.1f} '.format(int(channel), attenuation))
        #Clear the confirmation line (maybe should error check it?)
        print(self.read())
        

#Create a view to a single spiner box
class DASingleChannelView(QtGui.QDoubleSpinBox):
    def __init__(self, DA, channel):
        super(DASingleChannelView, self).__init__()
        self.DA = DA
        self.channel = channel
        
        self.setRange(self.DA.minAttenuation, self.DA.maxAttenuation)
        self.setValue(self.DA.getAttenuation(self.channel))
        self.valueChanged.connect(lambda value: self.DA.setAttenuation(self.channel, value))
#        self.show()
        
#Create a view for the whole board
class DAWholeBoardView(QtGui.QWidget):
    def __init__(self, DA):
        super(DAWholeBoardView, self).__init__()
        self.DA = DA
        
        vbox = QtGui.QVBoxLayout()
        for tmpChannel in range(1,self.DA.maxChannels+1):
            tmphbox = QtGui.QHBoxLayout()
            tmphbox.addStretch(1)
            tmphbox.addWidget(QtGui.QLabel('Channel {0}'.format(tmpChannel)))
            tmphbox.addWidget(DASingleChannelView(self.DA, tmpChannel))
            vbox.addLayout(tmphbox)

        self.setLayout(vbox)        
        self.show()
        
    
if __name__ == '__main__':
    print('Got here')
    da = DigitalAttenuator('COM4')
    
    app = QtGui.QApplication(sys.argv)
    tmpFont = QtGui.QFont()
    tmpFont.setPointSize(12)
    app.setFont(tmpFont)    
    
    DAView = DAWholeBoardView(da)
    sys.exit(app.exec_())


