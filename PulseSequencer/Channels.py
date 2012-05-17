'''
Channels is where we store information for mapping virtual (qubit) channel to real channels.

Created on Jan 19, 2012

@author: cryan


'''

import sys
import json

from PySide import QtGui, QtCore

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
    (logical, physical) = range(2)
    
class LogicalChannel(object):
    '''
    The main class from which we will generate sequences.  At some point it needs to be assigned to a physical channel.
    '''
    def __init__(self, name=None, channelType=None, physicalChannel=None):
        self.name = name
        self.channelType = channelType
        self.physicalChannel = physicalChannel
        
    @property
    def isLogical():
        return True
        
    @property
    def isPhysical():
        return False

class PhysicalChannel(object):
    '''
    The main class for actual AWG channels.
    '''
    def __init__(self, name=None, AWGName=None, channelType=None):
        self.name = name
        self.channelType = channelType
        self.AWGName = AWGName

    @property
    def isLogical():
        return False
        
    @property
    def isPhysical():
        return True


class PhysicalMarkerChannel(PhysicalChannel):
    '''
    An digital output channel on an AWG.
    '''
    def __init__(self, name=None, AWGName=None, channel=None, channelShift=0.0, **kwargs):
        super(PhysicalMarkerChannel, self).__init__(name=name, AWGName=AWGName, channelType=ChannelTypes.marker)
        self.channelType = ChannelTypes.marker
        self.channelShift = channelShift
        self.channel = channel
        
class QuadratureChannel(PhysicalChannel):
    '''
    Something used to implement a standard qubit channel with two analog channels and a microwave gating channel.
    '''
    def __init__(self, name=None, AWGName=None, carrierGen=None, IChannel=None, QChannel=None, gateChannel=None, gateBuffer=0.0, gateMinWidth=0.0, channelShift=0.0, gateChannelShift=0.0, correctionT = None, **kwargs):
        super(QuadratureChannel, self).__init__(name=name, AWGName=AWGName, channelType=ChannelTypes.quadratureMod)
        self.carrierGen = carrierGen
        self.IChannel = IChannel
        self.QChannel = QChannel
        self.gateChannel = gateChannel
        self.gateBuffer = gateBuffer
        self.gateMinWidth = gateMinWidth
        self.channelShift = channelShift
        self.gateChannelShift = gateChannelShift
        self.correctionT = [[1,0],[0,1]] if correctionT is None else correctionT
        
class LogicalMarkerChannel(LogicalChannel):
    '''
    A class for digital channels for gating sources or triggering other things.
    '''
    def __init__(self, name=None, physicalChannel=None, **kwargs):
        super(LogicalMarkerChannel, self).__init__(name=name, channelType=ChannelTypes.marker, physicalChannel=physicalChannel)        
    
    def gatePulse(self, length, delay=0):
        tmpBlock = PulseSequencer.PulseBlock()
        if delay>0:
            tmpBlock.add_pulse(PatternGen.QId(delay), self)
        tmpBlock.add_pulse(PatternGen.Square(length, amp=1), self)
        return tmpBlock
        
class QubitChannel(LogicalChannel):
    '''
    The main class for generating qubit pulses.  
    '''
    def __init__(self, name=None, physicalChannel=None, freq=None, piAmp=0.0, pi2Amp=0.0, pulseType='gauss', pulseLength=0.0, bufferTime=0.0, dragScaling=0, **kwargs):
        super(QubitChannel, self).__init__(name=name, channelType=ChannelTypes.quadratureMod, physicalChannel=physicalChannel)
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
    
def load_channel_dict(fileName=None):
    '''
    Helper function to convert back from a JSON file to a channel dictionary
    '''
    with open(fileName,'r') as FID:
        return json.load(FID)
        
def load_channel_info(fileName=None):
    '''
    Helper function to load a channel info file into channel and channelInfo objects
    '''
    channels = {}
    #First load the file into a dictionary
    channelDicts = load_channel_dict(fileName)
    for channelName, channelDict in channelDicts.items():
        channelType = channelDict['channelType']
        #Deal with logical channels
        if channelDict['isLogical']:
            if channelType == 'quadratureMod':
                #Create the qubit channel
                channelFunc = QubitChannel
            elif channelType == 'marker':
                #Create the marker channel
                channelFunc = LogicalMarkerChannel
        else:
            if channelType == 'quadratureMod':
                channelFunc = QuadratureChannel
            elif channelType == 'marker':
                channelFunc = PhysicalMarkerChannel

        channels[channelName] = channelFunc(**channelDict)

    return channels, channelDicts
    
'''    
*****************************************************************************
GUI Stuff.
*****************************************************************************
'''
class ChannelInfoView(QtGui.QMainWindow):
    def __init__(self, fileName):
        super(ChannelInfoView, self).__init__()
        
        #Load the channel information from the file
        self.channelDict = load_channel_dict(fileName)
        
        #Create an item view for the logical channels
        self.logicalChannelListModel = QtGui.QStringListModel([tmpKey for tmpKey in self.channelDict.keys() if channelDict[tmpKey]['isLogical']])
        self.logicalChannelListModel.sort(0)
        self.logicalChannelListView = QtGui.QListView()
        self.logicalChannelListView.setModel(self.logicalChannelListModel)
        self.logicalChannelListView.clicked.connect(self.update_channelView_logical)
        
        #Create an item view for the physical channels
        self.physicalChannelListModel = QtGui.QStringListModel([tmpKey for tmpKey in self.channelDict.keys() if channelDict[tmpKey]['isPhysical']])
        self.physicalChannelListModel.sort(0)
        self.physicalChannelListView = QtGui.QListView()
        self.physicalChannelListView.setModel(self.physicalChannelListModel)
        self.physicalChannelListView.clicked.connect(self.update_channelView_physical)

        tmpWidget = QtGui.QWidget()
        vBox = QtGui.QVBoxLayout(tmpWidget)
        
        tmpWidget2 = QtGui.QWidget()
        vBox2 = QtGui.QVBoxLayout(tmpWidget2)
        vBox2.addWidget(QtGui.QLabel('Logical Channels:'))
        vBox2.addWidget(self.logicalChannelListView)     

        tmpWidget3 = QtGui.QWidget()
        vBox3 = QtGui.QVBoxLayout(tmpWidget3)
        vBox3.addWidget(QtGui.QLabel('Physical Channels:'))
        vBox3.addWidget(self.physicalChannelListView)     


        vSplitter = QtGui.QSplitter()
        vSplitter.setOrientation(QtCore.Qt.Vertical)
        vSplitter.addWidget(tmpWidget2)        
        vSplitter.addWidget(tmpWidget3)        
        vBox.addWidget(vSplitter)

        #Add the buttons for adding/deleting channels
        hBox = QtGui.QHBoxLayout()
        hBox.addWidget(QtGui.QPushButton('Add'))
        hBox.addWidget(QtGui.QPushButton('Delete'))
        hBox.addStretch(1)
        vBox.addLayout(hBox)                

        #Setup the main splitter between the channel lists and channel properties
        hSplitter = QtGui.QSplitter()
        hSplitter.addWidget(tmpWidget)
        self.channelWidgets = {}
        for tmpChanName, tmpChan in self.channelDict.items():
            self.channelWidgets[tmpChanName] = ChannelView(tmpChan)
            hSplitter.addWidget(self.channelWidgets[tmpChanName])
            self.channelWidgets[tmpChanName].hide()
        
        self.setCentralWidget(hSplitter)
        
        self.setGeometry(300,300,550,300)
        self.setWindowTitle('Channel Info.')
        self.show()
        
        
    def update_channelView_logical(self, index):
        for tmpWidget in self.channelWidgets.values():
            tmpWidget.hide()
        
        tmpChan = self.logicalChannelListModel.data(index, QtCore.Qt.DisplayRole)
        self.channelWidgets[tmpChan].show()
        self.physicalChannelListView.clearSelection()
        
    def update_channelView_physical(self, index):
        for tmpWidget in self.channelWidgets.values():
            tmpWidget.hide()
        
        tmpChan = self.physicalChannelListModel.data(index, QtCore.Qt.DisplayRole)
        self.channelWidgets[tmpChan].show()
        self.logicalChannelListView.clearSelection()
        
        
class ChannelView(QtGui.QWidget):
    def __init__(self, channel):
        super(ChannelView, self).__init__()
        self.channel = channel
        
        #Setup a dictionary showing which fields to show and which to hide
#        self.showFields = {}
#        self.showFields['direct'] =         
        
        skipFields = ['channelType', 'name', 'isLogical', 'isPhysical']
        #Create the layout as a vbox of hboxes
        form = QtGui.QFormLayout()
        self.GUIhandles = {}
        #Do the channelType on top
        form.addRow('channelType', QtGui.QLabel(channel['channelType']))
        
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
    channelDict['q1'] = {'name':'q1', 'channelType':'quadratureMod', 'isLogical':True, 'isPhysical':False, 'piAmp':1.0, 'pi2Amp':0.5, 'pulseType':'drag', 'pulseLength':40e-9, 'bufferTime':2e-9, 'dragScaling':1, 'physicalChannel':'TekAWG1-12'}
    channelDict['q2'] = {'name':'q2', 'channelType':'quadratureMod', 'isLogical':True, 'isPhysical':False, 'piAmp':1.0, 'pi2Amp':0.5, 'pulseType':'drag', 'pulseLength':40e-9, 'bufferTime':2e-9, 'dragScaling':1, 'physicalChannel':'TekAWG1-34'}

    channelDict['measChannel'] = {'name':'measChannel', 'channelType':'marker', 'isLogical':True, 'isPhysical':False, 'physicalChannel':'TekAWG1-ch3m1' }
    channelDict['digitizerTrig'] = {'name':'digitizerTrig','channelType':'marker', 'isLogical':True, 'isPhysical':False, 'physicalChannel':'TekAWG1-ch3m2'}

    channelDict['TekAWG1-12'] = {'name':'TekAWG1-12', 'channelType':'quadratureMod', 'isLogical':False, 'isPhysical':True, 'AWGName':'TekAWG1', 'IChannel':'ch1', 'QChannel':'ch2', 'gateChannel':'ch1m1', 'channelShift':0e-9, 'gateChannelShift':0.0, 'gateBuffer':20e-9, 'gateMinWidth':100e-9, 'correctionT':[[1,0],[0,1]]}
    channelDict['TekAWG1-34'] = {'name':'TekAWG1-34', 'channelType':'quadratureMod', 'isLogical':False, 'isPhysical':True, 'AWGName':'TekAWG1', 'IChannel':'ch3', 'QChannel':'ch4', 'gateChannel':'ch4m1', 'channelShift':0e-9, 'gateChannelShift':0.0, 'gateBuffer':20e-9, 'gateMinWidth':100e-9, 'correctionT':[[1,0],[0,1]]}
    channelDict['TekAWG1-ch3m1'] = {'name':'TekAWG1-ch3m1', 'channelType':'marker', 'isLogical':False, 'isPhysical':True, 'AWGName':'TekAWG1', 'channel':'ch3m1', 'channelShift':0e-9 }    
    channelDict['TekAWG1-ch3m2'] = {'name':'TekAWG1-ch3m2', 'channelType':'marker', 'isLogical':False, 'isPhysical':True, 'AWGName':'TekAWG1', 'channel':'ch3m2', 'channelShift':0e-9 }
    
    save_channel_info(channelDict, 'ChannelParams.json')
    
    channelInfoBack = load_channel_dict('ChannelParams.json')
    
    app = QtGui.QApplication(sys.argv)

#    silly = PhysicalChannelView(channelInfo['APS1-12'])
#    silly.show()

    silly = ChannelInfoView('ChannelParams.json')
    
    sys.exit(app.exec_())

    
    