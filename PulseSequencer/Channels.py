'''
Channels is where we store information for mapping virtual (qubit) channel to real channels.

Created on Jan 19, 2012

@author: cryan


'''

import sys
import json

from PySide import QtGui

from operator import itemgetter

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
        self.correctionT = [[1,0],[0,1]]
    
        
class QuadratureChannel(object):
    '''
    Something closer to the hardware. i.e. it is associated with AWG channels and generators.
    '''
    def __init__(self, name=None, AWGName=None, carrierGen=None, IChannel=None, QChannel=None, gateChannel=None, gateBuffer=0.0, gateMinWidth=0.0, channelShift=0.0, gateChannelShift=0.0, correctionT = None):
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
        self.correctionT = [[1,0],[0,1]] if correctionT is None else correctionT
        
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
        self.pulseCache = {}
        
    def cachedPulse(pulseFunc):
        def cacheWrap(self):
            if pulseFunc.__name__ not in self.pulseCache:
                self.pulseCache[pulseFunc.__name__] = pulseFunc(self)
            return self.pulseCache[pulseFunc.__name__]
        
        return cacheWrap

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
    @cachedPulse
    def X180(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.piAmp, dragScaling=self.dragScaling, phase=0)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @cachedPulse
    def X90(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.pi2Amp, dragScaling=self.dragScaling, phase=0)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
    
    @cachedPulse
    def Xm180(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.piAmp, dragScaling=self.dragScaling, phase=0.5)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @cachedPulse
    def Xm90(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.pi2Amp, dragScaling=self.dragScaling, phase=0.5)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @cachedPulse
    def Y180(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.piAmp, dragScaling=self.dragScaling, phase=0.25)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @cachedPulse
    def Y90(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.pi2Amp, dragScaling=self.dragScaling, phase=0.25)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
       
    @cachedPulse
    def Ym180(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.piAmp, dragScaling=self.dragScaling, phase=0.75)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
    @cachedPulse
    def Ym90(self):
        tmpPulse = PatternGen.pulseDict[self.pulseType](time=self.pulseLength, cutoff=2, bufferTime=self.bufferTime, amp=self.pi2Amp, dragScaling=self.dragScaling, phase=0.75)
        tmpBlock = PulseSequencer.PulseBlock()
        tmpBlock.add_pulse(tmpPulse, self)
        return tmpBlock
        
        
def save_channel_info(channelDict, fileName=None):
    '''
    Helper function to save a channelInfo dictionary to a JSON file or string.
    '''
    #Convert the channel into a dictionary
    if fileName is None:
        return json.dumps(channelDict, sort_keys=True, indent=2)
    else:
        with open(fileName,'w') as FID:
            json.dump(channelDict, FID, sort_keys=True, indent=2)
    
def load_channel_info(fileName=None):
    '''
    Helper function to convert back from a JSON file to a channel object
    
    '''
    with open(fileName,'r') as FID:
        return json.load(FID)

class ChannelInfoView(QtGui.QMainWindow):
    def __init__(self, fileName):
        super(ChannelInfoView, self).__init__()
        
        #Load the channel information from the file
        self.channelDict = load_channel_info(fileName)
        
        #Create an item view for the channels
        self.channelListModel = QtGui.QStringListModel(sorted(self.channelDict.keys()))
        self.channelListView = QtGui.QListView()
        self.channelListView.setModel(self.channelListModel)
        
        #Connect 
        self.channelListView.clicked.connect(self.updateChannelView)
        
        tmpWidget = QtGui.QWidget()
        vBox = QtGui.QVBoxLayout(tmpWidget)
        vBox.addWidget(self.channelListView)
        hBox = QtGui.QHBoxLayout()
        hBox.addWidget(QtGui.QPushButton('Add'))
        hBox.addWidget(QtGui.QPushButton('Delete'))
        hBox.addStretch(1)
        vBox.addLayout(hBox)                
        self.hsplitter = QtGui.QSplitter()
        self.hsplitter.addWidget(tmpWidget)
        self.channelWidgets = {}
        for tmpChanName, tmpChan in self.channelDict.items():
            self.channelWidgets[tmpChanName] = ChannelView(tmpChan)
            self.hsplitter.addWidget(self.channelWidgets[tmpChanName])
            self.channelWidgets[tmpChanName].hide()
        
        self.setCentralWidget(self.hsplitter)
        self.updateChannelView()
        
        self.setGeometry(300,300,600,300)
        self.show()
        
        
    def updateChannelView(self):
        for tmpChanName in self.channelDict.keys():
            self.channelWidgets[tmpChanName].hide()

        tmpChan = self.channelListModel.stringList()[self.channelListView.currentIndex().row()]
        self.channelWidgets[tmpChan].show()
        
        
class ChannelView(QtGui.QWidget):
    def __init__(self, channel):
        super(ChannelView, self).__init__()
        self.channel = channel
        
        #Setup a dictionary showing which fields to show and which to hide
#        self.showFields = {}
#        self.showFields['direct'] =         
        
        skipFields = ['channelType', 'name']
        #Create the layout as a vbox of hboxes
        form = QtGui.QFormLayout()
        self.GUIhandles = {}
        #Do the channelType on top
        self.GUIhandles['channelType'] = QtGui.QComboBox()
        self.GUIhandles['channelType'].addItems(['direct', 'marker', 'amplitudeMod', 'quadratureMod'])
        self.GUIhandles['channelType'].setCurrentIndex(getattr(ChannelTypes, channel['channelType']))
        form.addRow('channelType', self.GUIhandles['channelType'])
        
        for key,value in sorted(channel.items(), key=itemgetter(0)):
            if key not in skipFields:
                if isinstance(value, basestring):
                    tmpWidget = QtGui.QLineEdit(value)
                else:
                    tmpWidget = QtGui.QLineEdit(str(value))
                    tmpWidget.setValidator(QtGui.QDoubleValidator())
                form.addRow(key, tmpWidget)
                self.GUIhandles[key] = tmpWidget
        self.setLayout(form)
            
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

    
    

if __name__ == '__main__':
    channelDict = {}
    channelDict['q1'] = {'name':'q1', 'channelType':'quadratureMod', 'piAmp':1.0, 'pi2Amp':0.5, 'pulseType':'drag', 'pulseLength':40e-9, 'bufferTime':2e-9, 'dragScaling':1, 'AWGName':'TekAWG1', 'IChannel':'ch1', 'QChannel':'ch2', 'gateChannel':'ch1m1', 'channelShift':0e-9, 'gateChannelShift':0.0, 'gateBuffer':20e-9, 'gateMinWidth':100e-9}
    channelDict['q2'] = {'name':'q2', 'channelType':'quadratureMod', 'piAmp':1.0, 'pi2Amp':0.5, 'pulseType':'drag', 'pulseLength':40e-9, 'bufferTime':2e-9, 'dragScaling':1, 'AWGName':'TekAWG1', 'IChannel':'ch1', 'QChannel':'ch2', 'gateChannel':'ch1m1', 'channelShift':0e-9, 'gateChannelShift':0.0, 'gateBuffer':20e-9, 'gateMinWidth':100e-9}

    channelDict['measChannel'] = {'name':'measChannel', 'channelType':'marker', 'AWGName':'TekAWG1', 'channel':'ch3m1' }
    channelDict['digitizerTrig'] = {'name':'digitizerTrig','channelType':'marker', 'AWGName':'TekAWG1', 'channel':'ch3m1', 'channelShift':-100e-9 }

    
    save_channel_info(channelDict, 'ChannelParams.json')
    
    
        
    channelInfoBack = load_channel_info('ChannelParams.json')
    
    app = QtGui.QApplication(sys.argv)

#    silly = PhysicalChannelView(channelInfo['APS1-12'])
#    silly.show()

    silly = ChannelInfoView('ChannelParams.json')
    
    sys.exit(app.exec_())

    
    