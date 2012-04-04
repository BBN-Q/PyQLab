'''
Created on Jan 8, 2012

Main classes for compiling pulse sequences.

@author: cryan
'''

from copy import deepcopy

import numpy as np

import ChannelInfo

AWGFreq = 1e9



class PulseBlock(object):
    '''
    The basic building block for pulse sequences. This is what we can concatenate together to make sequences.
    We also overload the + operator so that we can combine pulse blocks:
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
            
    #The maximum number of points needed for any channel on this block
    @property
    def maxPts(self):
        maxPts = 0
        for tmpPulseList in self.pulses.values():
            tmpPts = 0
            for tmpPulse in tmpPulseList:
                tmpPts += tmpPulse.numPoints(AWGFreq)
            maxPts = max(maxPts, tmpPts)
        return maxPts
    


class PulseSequence(object):
    '''
    A collection of pulse blocks which forms a sequence.
    '''
    
    
class LLElement(object):
    def __init__(self):
        self.key = None
        self.length = 0
        self.repeat =0
        self.isTimeAmplitude = False
        self.isZero = False
        self.hasTrigger = False
        self.linkListRepeat = 0

def create_padding_LL():
    tmpLL = LLElement()
    tmpLL.isTimeAmplitude = True
    tmpLL.isZero = True
    return tmpLL
    
    
def compile_sequence(pulseSeq, AWGFreq):
    '''
    Main function to compile a pulse sequence.
    This is where all the hard work is.  
    
    This is largely built around the APS model of waveforms and linklist specifying the sequence.
    However, it translates just fine to Tektronix too but the the waveform restrictions are global. 
    
    '''

    minWFPts = 16
    minStepPts = 4
    
    #Create a library of waveforms so that we don't repeat
    WFLibrary = {}
    
    #Sort out which channels we have to deal with an initialize the waveforms
    logicalLLs = {}
    for tmpBlock in pulseSeq:
        for tmpChan in tmpBlock.channels:
            if tmpChan.name not in logicalLLs:
                logicalLLs[tmpChan.name] = []
                    
    emptyLLs = deepcopy(logicalLLs)

    #Loop over each of the pulse sequence blocks
    #Generate the shapes and build the waveform library
    #Then parse the paddings according to the alignment
    for tmpBlock in pulseSeq:
        tmpLLs = deepcopy(emptyLLs)
        
        #Add the initial paddings
        for tmpLL in tmpLLs.values():
            tmpLL.append(create_padding_LL())
            
        #Loop over each channel in the block and add LL elements
        for tmpChanName in tmpBlock.channelNames:
            for tmpPulse in tmpBlock.pulses[tmpChanName]:
                if id(tmpPulse) not in WFLibrary:
                    WFLibrary[id(tmpPulse)] = tmpPulse.generatePattern(AWGFreq)
                tmpLL = LLElement()
                tmpLL.key = id(tmpPulse)
                tmpLL.length = tmpPulse.numPoints(AWGFreq)
                tmpLLs[tmpChanName].append(tmpLL)
            
        #Add the final paddings
        for tmpLL in tmpLLs.values():
            tmpLL.append(create_padding_LL())
        

        #Now adjust the paddings according the pulse block alignment
        maxPts = tmpBlock.maxPts
        for tmpLL in tmpLLs.values():
            numPts = 0
            for tmpElement in tmpLL:
                numPts += tmpElement.length
            padLength = numPts-maxPts
            if tmpBlock.alignment == 'left':
                #We pad the final LL element
                tmpLL[-1].repeat = padLength
            elif tmpBlock.alignment == 'right':
                #We pad the first LL element
                tmpLL[0].repeat = padLength
            elif tmpBlock.alignment == 'center':
                #We split the difference
                tmpLL[0].repeat = padLength//2
                tmpLL[-1].repeat = padLength//2 + 1 if np.mod(padLength,2) else padLength//2
        
        #Trim empty paddings
        for tmpLL in tmpLLs.values():
            if tmpLL[0].repeat == 0:
                del tmpLL[0]
            if tmpLL[-1].repeat == 0:
                del tmpLL[-1]
        
        #Append this block onto the total pulse sequence
        for tmpName, tmpLL in logicalLLs.items():
            tmpLL += tmpLLs[tmpName]
        
    
            
    return logicalLLs, WFLibrary


def TekChannels():
    '''
    The set of channels for a Tektronix AWG
    '''
    return {'Ch1':None, 'Ch2':None, 'Ch3':None, 'Ch4':None, 'Ch1M1':None, 'Ch1M2':None, 'Ch2M1':None, 'Ch2M2':None , 'Ch3M1':None, 'Ch3M2':None , 'Ch4M1':None, 'Ch4M2':None}
                    
def compile_LLs(logicalLLs, WFLibrary, channelInfo):
    '''
    Final compiling steps which translates from logical channels to physical channels.
    '''
    #TODO: allow multiple logical channels to map onto physical channels for APS
    AWGTypes = {'TekAWG':'Tektronix', 'BBNAPS':'APS'}
    
    WFLibrary = {}
    
    #Loop through each of the logical channels
    for tmpChanName, LLs in logicalLLs.items():
        #Deal with the different channeltypes
        tmpChanType = channelInfo[tmpChanName].channelType
        if tmpChanType == ChannelInfo.ChannelTypes.quadratureMod:
            #First do the real part of the analog part
            realChan = channelInfo[channelInfo[tmpChanName].physicalChannel]
            
            
    
    
    #For each of the instruments create the zero channels
    for instrument in channelInfo.instrumentList:
        
     
    
    
                        
                    
def LLtoSequence(LL, WFLibrary):
    '''
    Helper function for converting a LL to a single sequence array for plotting or Tektronix purposes.
    '''
    #Count up how much space we need
    numPts = 0
    for tmpLLElement in LL:
        numPts += tmpLLElement.length
    
    #Allocate the array
    outSeq = np.zeros(numPts,dtype=np.complex128)
    
    idx = 0
    for tmpLLElement in LL:
        outSeq[idx:idx+tmpLLElement.length] = WFLibrary[tmpLLElement.key]
        idx += tmpLLElement.length
    
    return outSeq
    
    
    
                    

                

                
        
    

"""
def CompileSequence(pulseSeq, channelInfo):
    '''
    Main function to compile a pulse sequence.
    This is where all the hard work is.  
    '''
    
    #Sort out which channels we have to deal with an initialize the waveforms
    LogicalLLs = {}
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
        
def compile_sequences(pulseSeqs, channelInfo):
    AWGWFs = []
    for pulseSeq in pulseSeqs:
        AWGWFs.append(compile_sequence(pulseSeq, channelInfo))
        

def loadChannelInfo(dataFile, channel):
    pass
        

    
    
if __name__ == '__main__':
    
#    #Load the channel information from file
#    channelInfo = loadChannelInfo('channelInfo.dat', 'q1')
#    
#    q1 = channelInfo.channels['q1']
#    q2 = channelInfo.channels['q2']
    

    #Create a qubit channel
    q1 = ChannelInfo.QubitChannel(name='q1', physicalChannel=None, freq=None, piAmp=1.0, pi2Amp=0.5, pulseType='gauss', pulseLength=40e-9, bufferTime= 2e-9)

    
    #Define a typical sequence
    pulseSeq = [q1.X180, q1.X90]
    
    LLs, WFLibrary = compile_sequence(pulseSeq, AWGFreq)
    
