'''
ChannelInfo is where we store information for mapping virtual (qubit) channel to real channels.

Created on Jan 19, 2012

@author: cryan


'''

import sys
import json

from PySide import QtGui

import PatternGen
import PulseSequencer

class ChannelTypes(object):
    '''
    Enumerate the possible types:
    direct - goes straight to something i.e. no modulated carrier
    digital - a logical digital channel usually assigned to a marker channel
    amplitudeMod - an amplitude modulated carrier
    quadratureMod - a quadrature modulated carrier
    '''
    (direct, marker, amplitudeMod, quadratureMod) = range(4)
    
class AnalogChannel(object):
    '''
    An analog output channel.
    '''
    def __init__(self, name=None, offset=0.0, delay=0.0):
        self.channelType = ChannelTypes.amplitudeMod        
        self.name = name
        self.offset = offset
        self.delay = delay
        
class PhysicalMarkerChannel(object):
    '''
    An digital output channel.
    '''
    def __init__(self, name=None, channelShift=0.0, AWGName=None, channel=None):
        self.channelType = ChannelTypes.marker
        self.name = name
        self.channelShift = channelShift
        self.AWGName = AWGName
        self.channel = channel
    
        
class QuadratureChannel(object):
    '''
    Something closer to the hardware. i.e. it is associated with AWG channels and generators.
    '''
    def __init__(self, name=None, AWGName=None, carrierGen=None, IChannel=None, QChannel=None, gateChannel=None, gateBuffer=0.0, gateMinWidth=0.0, channelShift=0.0, gateChannelShift=0.0):
        self.name = name
        self.channelType = ChannelTypes.quadratureMod
        self.AWGName = AWGName
        self.carrierGen = carrierGen
        self.IChannel = IChannel
        self.QChannel = QChannel
        self.gateChannel = gateChannel
        self.gateBuffer = gateBuffer
        self.gateMinWidth = gateMinWidth
        self.channelShift = channelShift
        self.gateChannelShift = gateChannelShift
        
class PhysicalChannelView(QtGui.QWidget):
    def __init__(self, channel):
        super(PhysicalChannelView, self).__init__()
        self.channel = channel
        
        skipFields = ['__class__']
        #Create the layout as a vbox of hboxes
        vbox = QtGui.QVBoxLayout()
        self.GUIhandles = {}
        for key,value in self.channel.__dict__.items():
            if key not in skipFields:
                tmpHBox = QtGui.QHBoxLayout()
                tmpHBox.addStretch(1)
                tmpHBox.addWidget(QtGui.QLabel(key))
                if key == 'channelType':
                    tmpWidget = QtGui.QComboBox()
                    tmpWidget.addItems(['direct', 'digital', 'amplitudeMod', 'quadratureMod'])
                    tmpWidget.setCurrentIndex(getattr(ChannelTypes, value))
                    tmpHBox.addWidget(tmpWidget)
                elif isinstance(value, basestring):
                    tmpWidget = QtGui.QLineEdit(value)
                    tmpHBox.addWidget(tmpWidget)
                else:
                    tmpWidget = QtGui.QLineEdit(str(value))
                    tmpWidget.setValidator(QtGui.QDoubleValidator())
                    tmpHBox.addWidget(tmpWidget)
                vbox.addLayout(tmpHBox)
                self.GUIhandles[key] = tmpWidget
        self.setLayout(vbox)
            
    def updateFromGUI(self):
        '''
        Update the channel object with the current values
        '''
        for key,tmpWidget in self.GUIhandles.items():
            if key == 'channelType':
                setattr(self.channel, key, tmpWidget.currentText())
            elif isinstance(getattr(self.channel, key), basestring):
                setattr(self.channel, key, tmpWidget.text())
            else:
                setattr(self.channel, key, float(tmpWidget.text()))
                
                
class LogicalMarkerChannel(object):
    '''
    A class for digital channels for gating sources or triggering other things.
    '''
    def __init__(self,name=None):
        self.name = name
    
    def gatePulse(self, length, delay=0):
        tmpBlock = PulseSequencer.PulseBlock()
        if delay>0:
            tmpBlock.add_pulse(PatternGen.QId(delay), self)
        tmpBlock.add_pulse(PatternGen.Square(length, amp=1), self)
        return tmpBlock
        
        
class LogicalChannel(object):
    '''
    The main class to which we assign points.  At some point it needs to be assigned to a physical channel.
    '''
    def __init__(self, name=None, channelType=None, physicalChannel=None, freq=None):
        self.name = name
        self.channelType = channelType
        self.physicalChannel = physicalChannel
        self.freq = freq
        
class QubitChannel(LogicalChannel):
    '''
    An extension of a logical channel with some calibrations and default pulses
    '''
    def __init__(self, name=None, physicalChannel=None, freq=None, piAmp=0.0, pi2Amp=0.0, pulseType='gauss', pulseLength=0.0, bufferTime=0.0, dragScaling=0):
        super(QubitChannel, self).__init__(name=name, channelType=ChannelTypes.quadratureMod, physicalChannel=physicalChannel, freq=freq)
        self.pulseType = pulseType
        self.pulseLength = pulseLength
        self.bufferTime = bufferTime
        self.piAmp = piAmp
        self.pi2Amp = pi2Amp
        self.dragScaling = dragScaling


    '''
    Setup some common pulses.
    '''    
    
    #A delay or do-nothing
    def QId(self, delay=0):
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(PatternGen.QId(delay), self)    
        return tmpBlock
        
    #A generic X rotation with a variable amplitude
    def Xtheta(self, amp=0):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=amp, dragScaling=self.dragScaling, phase=0)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock

    #A generic X rotation with a variable amplitude
    def Ytheta(self, amp=0):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=amp, dragScaling=self.dragScaling, phase=0.25)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        

    
    '''
    Setup the default 90/180 rotations
    '''
    @property
    def X180(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.piAmp, dragScaling=self.dragScaling, phase=0)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @property
    def X90(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.pi2Amp, dragScaling=self.dragScaling, phase=0)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
    
    @property
    def Xm180(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.piAmp, dragScaling=self.dragScaling, phase=0.5)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @property
    def Xm90(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.pi2Amp, dragScaling=self.dragScaling, phase=0.5)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @property
    def Y180(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.piAmp, dragScaling=self.dragScaling, phase=0.25)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @property
    def Y90(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.pi2Amp, dragScaling=self.dragScaling, phase=0.25)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
       
    @property
    def Ym180(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.piAmp, dragScaling=self.dragScaling, phase=0.75)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @property
    def Ym90(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.pi2Amp, dragScaling=self.dragScaling, phase=0.75)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
        
def saveChannelInfo(channelInfo, fileName=None):
    '''
    Helper function to save a channelInfo dictionary to a JSON file or string.
    '''
    #Convert the channel into a dictionary
    tmpDict = {}
    for tmpChanName, tmpChan in channelInfo.items():
        tmpDict[tmpChanName] =  tmpChan.__dict__
        tmpDict[tmpChanName]['__class__'] = tmpChan.__class__.__name__
        
    if fileName is None:
        return json.dumps(tmpDict, sort_keys=True, indent=2)
    else:
        with open(fileName,'w') as FID:
            json.dump(tmpDict, FID, sort_keys=True, indent=2)
    
def loadChannelInfo(fileName=None):
    '''
    Helper function to convert back from a JSON file to a channel object
    
    '''
    import sys
    curModule = sys.modules[__name__]
    with open(fileName,'r') as FID:
        tmpDict = json.load(FID)
        channelDict = {}
     
        for tmpChan in tmpDict.keys():
            channelClass = tmpDict[tmpChan].pop('__class__')
            tmpClass = getattr(curModule, channelClass)
            #Have to convert from unicode json returns
            args = dict( (key.encode('ascii'), value) for key, value in tmpDict[tmpChan].items())
            channelDict[tmpChan.encode('ascii')] = tmpClass(**args)
        
        return channelDict
        

class ChannelInfoView(QtGui.QMainWindow):
    def __init__(self, fileName):
        super(ChannelInfoView, self).__init__()
        
        #Load the channel information from the file
        self.channelDict = loadChannelInfo(fileName)
        
        #Create an item view for the channels
        self.channelListModel = QtGui.QStringListModel(self.channelDict.keys())
        self.channelListView = QtGui.QListView()
        self.channelListView.setModel(self.channelListModel)
        
        #Connect 
        self.channelListView.clicked.connect(self.updateChannelView)
        
        self.hsplitter = QtGui.QSplitter()
        self.hsplitter.addWidget(self.channelListView)
#        self.hsplitter.addWidget(QtGui.QPushButton('Hello'))
        self.channelWidgets = {}
        for tmpChanName, tmpChan in self.channelDict.items():
            self.channelWidgets[tmpChanName] = PhysicalChannelView(tmpChan)
            self.hsplitter.addWidget(self.channelWidgets[tmpChanName])
            self.channelWidgets[tmpChanName].hide()
        
        self.setCentralWidget(self.hsplitter)
        self.updateChannelView()
        
        
    def updateChannelView(self):
        for tmpChanName in self.channelDict.keys():
            self.channelWidgets[tmpChanName].hide()

        tmpChan = self.channelListModel.stringList()[self.channelListView.currentIndex().row()]
        self.channelWidgets[tmpChan].show()
        
        
        
    
    

if __name__ == '__main__':
    channelInfo = {}
    channelInfo['Q1Chan'] = LogicalChannel(name='q1',channelType='quadratureMod', freq=4.258e9, physicalChannel='APS1-12')
    channelInfo['APS1-12'] = PhysicalChannel(name='APS12', channelType='quadratureMod', carrierGen='labBrick1',IChannel='BBNAPS1',QChannel='BBNAPS2',markerChannel='TekAWGCh3M1')
    
    saveChannelInfo(channelInfo, 'tmpFile.cfg')
    
    channelInfoBack = loadChannelInfo('tmpFile.cfg')
    
    app = QtGui.QApplication(sys.argv)

#    silly = PhysicalChannelView(channelInfo['APS1-12'])
#    silly.show()

    silly = ChannelInfoView('tmpFile.cfg')
    silly.show()
    
    sys.exit(app.exec_())

    
    