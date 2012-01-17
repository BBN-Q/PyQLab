'''
Created on Jan 8, 2012

Main classes for compiling pulse sequences.

@author: cryan
'''

from copy import deepcopy

import numpy as np


AWGFreq = 1e9
bufferTime = 2/1.e9

class ChannelTypes(object):
    '''
    Enumerate the possible types:
    direct - goes straight to something i.e. no modulated carrier
    digital - a logical digital channel usually assigned to a marker channel
    amplitudeMod - an amplitude modulated carrier
    quadratureMod - a quadrature modulated carrier
    '''
    (direct, digital, amplitudeMod, quadratureMod) = range(4)
    

class LogicalChannel(object):
    '''
    The main class to which we assign points.  At some point it needs to be assigned to a physical channel.
    '''
    def __init__(self, name=None, channelType=None, physicalChannel=None, freq=None):
        self.name = name
        self.channelType = channelType
        self.physicalChannel = physicalChannel
        self.freq = freq
        
class PhysicalChannel(object):
    '''
    Something closer to the hardware. i.e. it is associated with AWG channnels and generators.
    '''
    def __init__(self, name=None, channelType=None, carrierGen=None, IChannel=None, QChannel=None, markerChannel=None, delay=None):
        self.name = name
        self.channelType = channelType
        self.carrierGen = carrierGen
        self.IChannel = IChannel
        self.QChannel = QChannel
        self.markerChannel = markerChannel
        self.delay = delay
        

class PulseBlock(object):
    '''
    The basic building block for pulse sequences. This is what we can concatenate together to make sequences.
    We also overload the + operator so that we can combine pulse block:
     -same channels get concatenated 
     -different channels are added in parallel and then subsequently aligned by the pulse compiler
    '''
    def __init__(self):
        #Set some default values
        #How multiple channels are aligned.
        self.alignment = 'left'
        self.pulses = {}
        self.channels = []
        
    #A list of the channels used in this block
    @property
    def channelNames(self):
        return [channel.name for channel in self.channels]
    
    def add_pulse(self, pulse, channel):
        if channel in self.channels:
            self.pulses[channel.name] += pulse
        else:
            self.channels.append(channel)
            self.pulses[channel.name] = [pulse]
            
    #Overload the addition operator to combine pulse blocks
    def __add__(self, rhs):
        for channel in self.channels:
            self.add_pulse(rhs.pulses[channel.name])
            
        return self
            
    


class PulseSequence(object):
    '''
    A collection of pulse blocks which forms a sequence.
    '''
    
    
def CompileSequence(pulseSeq, channelInfo):
    '''
    Main function to compile a pulse sequence.
    This is where all the hard work is.  
    
    This is largely built around the APS model of waveforms and linklist specifying the sequence.
    However, it translates just fine to Tektronix too but the the waveform resrictions are global. 
    
    '''

    minWFPts = 16
    minStepPts = 4
    
    #Create a library of waveforms so that we don't repeat
    WFLibrary = []
    
    #Link list for the sequence for each 
    
    LLs {} 
    #Loop over each of the pulse sequence blocks generate the shapes and then parse the paddings as efficiently as possible
    for tmpBlock in pulseSeq:
        #Loop over each channel we need to deal with 
        
    

"""
def CompileSequence(pulseSeq, channelInfo):
    '''
    Main function to compile a pulse sequence.
    This is where all the hard work is.  
    '''
    
    #Sort out which channels we have to deal with an initialize the waveforms
    LogicalWFs = {}
    for tmpBlock in pulseSeq:
        for tmpChan in tmpBlock.channels:
            if tmpChan.name not in LogicalWFs:
                if tmpChan.channelType == ChannelTypes.quadratureMod:
                    LogicalWFs[tmpChan.name] = np.array([], dtype=np.complex128)
                elif tmpChan.channelType == ChannelTypes.digital:
                    LogicalWFs[tmpChan.name] = np.array([], dtype=np.bool)
                elif tmpChan.channelType == ChannelTypes.analogMod:
                    LogicalWFs[tmpChan.name] = np.array([], dtype=np.float64)
                elif tmpChan.channelType == ChannelTypes.direct:
                    LogicalWFs[tmpChan.name] = np.array([], dtype=np.float64)
                    
    EmptyWFs = deepcopy(LogicalWFs)
                    
    #Loop over each of the pulse sequence blocks and concatenate on the pattern or zero-fill if not defined. 
    for tmpBlock in pulseSeq:
        #Loop over each of the channels in the block
        tmpWFs = deepcopy(EmptyWFs)
        for tmpChanName in tmpWFs.keys():
            if tmpChanName in tmpBlock.channels:
                #Concatenate the pulse on
                tmpWFs[tmpChanName] = tmpBlock.channel[tmpChan.name].generatePattern(tmpChan.bufferTime, 1e9)
                
        #Pad each channel to align and concatenate onto the total waveform list
        maxNumPts = 0
        for tmpWF in tmpWFs.items():
            maxNumPts = max(maxNumPts, size)
        for tmpChanName in tmpWFs.keys():
            paddingPts = maxNumPts-tmpWFs[tmpChanName].sizes
            if paddingPts:
                if tmpBlock.alignment == 'left':
                    tmpWFs[tmpChanName] = np.hstack((tmpWFs[tmpChanName], np.zeros(paddingPts)))
                elif tmpBlock.alignment == 'right':
                    tmpWFs[tmpChanName] = np.hstack((np.zeros(paddingPts), tmpWFs[tmpChanName]))
                elif tmpBlock.alignment == 'centre':
                    if np.mod(paddingPts,2):
                        tmpWFs[tmpChanName] = np.hstack((np.zeros(paddingPts/2), tmpWFs[tmpChanName], np.zeros(paddingPts/2)))
                    else:
                        tmpWFs[tmpChanName] = np.hstack((np.zeros(paddingPts//2), tmpWFs[tmpChanName], np.zeros(paddingPts//2 + 1)))
                        
            LogicalWFs[tmpChanName] = np.hstack((LogicalWFs[tmpChanName], tmpWFs[tmpChanName]))
            
    
    #Delay the channels as necessary by zero padding the beginning and end
    #Also add gating pulses to the WF list if necessary here
    #First work out the maximum delay needed
    maxDelay = 0
    for tmpChanName in tmpWFs.keys():
        maxDelay = max(maxDelay, channelInfo.delays[tmpChanName])
        #Also check for gating delay on the gate line
        if channelInfo.gateChannel[tmpChanName] is not None:
            maxDelay = max(maxDelay, channelInfo.gateDelay[tmpChanName] + channelInfo.gateBuffer[tmpChanName])
    #Add one point to make sure we don't start high
    maxDelayPts = round(maxDelay*AWGFreq) + 1
    for tmpChanName in tmpWFs.keys():
        delayPts = round(channelInfo.delays[tmpChanName])
        #Add one point to make sure we don't finish high
        tmpWFs[tmpChanName] = np.hstack(np.zeros(maxDelayPts-delayPts), tmpWFs[tmpChanName], np.zeros(delayPts+1))
        
    #Convert the logical channels to AWG channels
    AWGWFs = {}
    for tmpChanName, tmpWF in tmpWFs.iteritems():
        tmpPhysChannel = channelInfo.physicalChannel[tmpChanName]
        if channelInfo.channelTypes[tmpChanName] == ChannelTypes.quadratureMod:
            #Apply any SSB necessary
            SSBFreq = channelInfo.freqs[tmpChanName] - tmpPhysChannel.freq
            if SSBFreq > 1e-12:
                timeStep = 1/AWGFreq
                tmpWF = np.exp(1j*2*pi*(SSBFreq)*np.arange(0, tmpWF.size*timeStep-1e-12, timeStep))*tmpWF
              
            AWGWFs[tmpPhysChannel.IChannel] = np.real(tmpWF)
            AWGWFs[tmpPhysChannel.QChannel] = np.imag(tmpWF)  
            
            #If we also have a marker channel associated with this channel then use it as a gating channel
            if tmpPhysChannel.markerChannel is not None:
                delayShift = round(channelInfo.gateDelay[tmpChanName]*AWGFreq)
                pulsePts = np.flatnonzero(tmpWF) - delayShift
                tmpGateWF = np.zeros(tmpWF.size, dtype=np.bool)
                tmpGateWF[pulsePts] = 1
                
                #Add any gate buffering
                onOffPts = np.diff(tmpGateWF).nonzero()[0]
                onOffPts.resize(2, onOffPts.size/2)
                bufferPts = round(channelInfo.gateBuffer[tmpChanName]*AWGFreq)
                for onPt, offPt in zip((onOffPts[0],onOffPts[1])):
                    tmpGateWF[onPt-bufferPts:offPt+bufferPts] = 1
                
                #Make sure we are respecting the gateReset minimum
                minGateSpacingPts = round(channelInfo.gateReset[tmpChanName]*AWGFreq)
                onOffPts = np.diff(tmpGateWF).nonzero()[0]
                onOffPts.resize(2, onOffPts.size/2)
                for gatect in range(onOffPts.shape[1]-1):
                    if (onOffPts[0,gatect+1] - onOffPts[1,gatect]) < minGateSpacingPts:
                        tmpGateWF[onOffPts[1,gatect]:onOffPts[0,gatect+1]] = 1
                        
                AWGWFs[tmpPhysChannel.markerChannel] = tmpGateWF 
                        
        elif channelInfo.channelTypes[tmpChanName] == ChannelTypes.digital:
            AWGWFs[tmpPhysChannel.markerChannel] = tmpWF
            
    return AWGWFs        

"""
        
def CompileMultipleSequences(pulseSeqs, channelInfo):
    AWGWFs = []
    for pulseSeq in pulseSeqs:
        AWGWFs.append(CompileSequence(pulseSeq, channelInfo))
        

def loadChannelInfo(dataFile, channel):
    pass
        

    
    
if __name__ == '__main__':
    
    #Load the channel information from file
    channelInfo = loadChannelInfo('channelInfo.dat', 'q1')
    
    q1 = channelInfo.channels['q1']
    q2 = channelInfo.channels['q2']
    
    #Define a typical sequence
    pulseSeq = [q1.Xp, q1.Xp + [q2.X90p + q2.Id(100e-9)]]
    
    AWGWFs = CompileSequence(pulseSeq, channelInfo)
    
