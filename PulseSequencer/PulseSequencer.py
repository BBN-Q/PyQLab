'''
Created on Jan 8, 2012

Main classes for compiling pulse sequences.

@author: cryan
'''

from copy import deepcopy

import numpy as np

import Channels

AWGFreq = 1e9

from TekPattern import write_Tek_file

from PulseSequencePlotter import plot_pulse_seqs



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
        for tmpChannel in rhs.channels:
            for tmpPulse in rhs.pulses[tmpChannel.name]:
                self.add_pulse(tmpPulse, tmpChannel)
        
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
        self.repeat = 1
        self.isTimeAmplitude = False
        self.isZero = False
        self.hasTrigger = False
        self.linkListRepeat = 0

def create_padding_LL():
    tmpLL = LLElement()
    tmpLL.isTimeAmplitude = True
    tmpLL.isZero = True
    return tmpLL
    
    
def compile_sequence(pulseSeq, WFLibrary = {}, AWGFreq = 1.2e9):
    '''
    Main function to compile a pulse sequence.
    This is where all the hard work is.  
    
    This is largely built around the APS model of waveforms and linklist specifying the sequence.
    However, it translates just fine to Tektronix too but the the waveform restrictions are global. 
    
    '''

    minWFPts = 16
    minStepPts = 4
    
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
                tmpLL = LLElement()
                if tmpPulse.isZero:
                    tmpLL.isZero = True
                    tmpLL.length = tmpPulse.numPoints(AWGFreq)
                else:
                    if id(tmpPulse) not in WFLibrary:
                        WFLibrary[id(tmpPulse)] = tmpPulse.generatePattern(AWGFreq)
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
            padLength = maxPts-numPts
            if tmpBlock.alignment == 'left':
                #We pad the final LL element
                tmpLL[-1].length = padLength
            elif tmpBlock.alignment == 'right':
                #We pad the first LL element
                tmpLL[0].length = padLength
            elif tmpBlock.alignment == 'centre':
                #We split the difference
                tmpLL[0].length = padLength//2
                tmpLL[-1].length = padLength//2 + 1 if np.mod(padLength,2) else padLength//2
        
        #Trim empty paddings
        for tmpLL in tmpLLs.values():
            if tmpLL[0].length == 0:
                del tmpLL[0]
            if tmpLL[-1].length == 0:
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
                    
def logical2hardware(pulseSeqs, WFLibrary, channelInfo):

    '''
    Final compiling steps which translates from logical channels to physical channels and adding gating pulses.
    '''
    #For each of the instruments create the zero channels
    hardwareLLs = {}
    for instrument in channelInfo['AWGList']:
        if instrument[:6] == 'TekAWG':
            hardwareLLs[instrument] = {}
            hardwareLLs[instrument]['ch1'] = []
            hardwareLLs[instrument]['ch1m1'] = []
            hardwareLLs[instrument]['ch1m2'] = []
            hardwareLLs[instrument]['ch2'] = []
            hardwareLLs[instrument]['ch2m1'] = []
            hardwareLLs[instrument]['ch2m2'] = []
            hardwareLLs[instrument]['ch3'] = []
            hardwareLLs[instrument]['ch3m1'] = []
            hardwareLLs[instrument]['ch3m2'] = []
            hardwareLLs[instrument]['ch4'] = []
            hardwareLLs[instrument]['ch4m1'] = []
            hardwareLLs[instrument]['ch4m2'] = []
            
        elif instrument[:6] == 'BBNAPS':
            hardwareLLs[instrument] = {}
            hardwareLLs[instrument]['ch1'] = {}
            hardwareLLs[instrument]['ch1']['LLs'] = []
            hardwareLLs[instrument]['ch2'] = {}
            hardwareLLs[instrument]['ch2']['LLs'] = []
            hardwareLLs[instrument]['ch3'] = {}
            hardwareLLs[instrument]['ch3']['LLs'] = []
            hardwareLLs[instrument]['ch4'] = {}
            hardwareLLs[instrument]['ch4']['LLs'] = []
            
        else:
            raise NameError('Unknown instrument type.')

    #Convert the complex LL and waveforms library into two real ones
    #Since the mixer imperfections mix the quadratures we have to create a library for each channel
    #This could be better (e.g. convert a quadrature WF that is all zeros to a TAZ entry)
    IWFLibrary = {}
    QWFLibrary = {}
    AWFLibrary = {}
    for tmpChanName in pulseSeqs[0].keys():
        IWFLibrary[tmpChanName] = {}
        QWFLibrary[tmpChanName] = {}
        AWFLibrary[tmpChanName] = {}
        
        for tmpKey, tmpWF in WFLibrary.items():
            IWFLibrary[tmpChanName][tmpKey] = tmpWF.real*channelInfo[tmpChanName].correctionT[0][0] + tmpWF.imag*channelInfo[tmpChanName].correctionT[0][1]
            QWFLibrary[tmpChanName][tmpKey] = tmpWF.imag*channelInfo[tmpChanName].correctionT[1][1]
            AWFLibrary[tmpChanName][tmpKey] = np.abs(tmpWF)

    #Loop through each pulse sequence
    for logicalLLs in pulseSeqs:
        
        #Reset the need zero WF flags
        seqLength = {}
        needZeroWF = {}
        for instrument in channelInfo['AWGList']:
            seqLength[instrument] = 0
            needZeroWF[instrument] = {}
            for tmpChanName in hardwareLLs[instrument].keys():
                needZeroWF[instrument][tmpChanName] = True
                
        #Deal with channelShifts here
        #Find out what the maximum channelShifts forward and backwards in time
        maxForwardShift = 0
        maxBackwardShift = 0
        
        #Sort out the delay buffering
        for tmpChanName in logicalLLs.keys():
            #Deal with the different channeltypes
            tmpChanType = channelInfo[tmpChanName].channelType
    
            if tmpChanType == Channels.ChannelTypes.quadratureMod:
                if channelInfo[tmpChanName].channelShift > 0:
                    maxForwardShift = max(maxForwardShift, channelInfo[tmpChanName].channelShift)
                else:
                    maxBackwardShift = max(maxBackwardShift, -channelInfo[tmpChanName].channelShift)
                if channelInfo[tmpChanName].gateChannelShift > 0:
                    maxForwardShift = max(maxForwardShift, channelInfo[tmpChanName].gateChannelShift)
                else:
                    maxBackwardShift = max(maxBackwardShift, -channelInfo[tmpChanName].gateChannelShift)
                
            elif tmpChanType == Channels.ChannelTypes.marker:
                if channelInfo[tmpChanName].channelShift > 0:
                    maxForwardShift = max(maxForwardShift, channelInfo[tmpChanName].channelShift)
                else:
                    maxBackwardShift = max(maxBackwardShift, -channelInfo[tmpChanName].channelShift)
        
        #Add a safety buffer for gate buffers and whatnot
        maxBackwardShift += 100e-9
        maxForwardShift += 100e-9
       
        #Loop through each of the logical channels and assign the LL to the appropriate 
        for tmpChanName, tmpLLSeq in logicalLLs.items():
            #Deal with the different channeltypes
            tmpChanType = channelInfo[tmpChanName].channelType
            tmpName = channelInfo[tmpChanName].AWGName
    
            
            #Quadrature channels require two analog channels        
            if tmpChanType == Channels.ChannelTypes.quadratureMod:
                #Switch on the type of AWG
                #TODO: deal with channel delays by inserting an additional zero element
                if tmpName[:6] == 'TekAWG':
                    tmpInitPad = create_padding_LL()
                    tmpFinalPad = create_padding_LL()

                    #I Channel
                    tmpInitPad.length = round(AWGFreq*(maxBackwardShift + channelInfo[tmpChanName].channelShift))                    
                    tmpFinalPad.length = round(AWGFreq*(maxForwardShift - channelInfo[tmpChanName].channelShift))                     
                    hardwareLLs[tmpName][channelInfo[tmpChanName].IChannel].append(LL2sequence([tmpInitPad] + tmpLLSeq + [tmpFinalPad], IWFLibrary[tmpChanName]))
                    needZeroWF[tmpName][channelInfo[tmpChanName].IChannel] = False
                    #Q Channel
                    hardwareLLs[tmpName][channelInfo[tmpChanName].QChannel].append(LL2sequence([tmpInitPad] + tmpLLSeq + [tmpFinalPad], QWFLibrary[tmpChanName]))
                    needZeroWF[tmpName][channelInfo[tmpChanName].QChannel] = False

                    #Gate channel
                    tmpInitPad.length = round(AWGFreq*(maxBackwardShift + channelInfo[tmpChanName].gateChannelShift))                    
                    tmpFinalPad.length = round(AWGFreq*(maxForwardShift - channelInfo[tmpChanName].gateChannelShift))                     
                    hardwareLLs[tmpName][channelInfo[tmpChanName].gateChannel].append(create_Tek_gate_seq([tmpInitPad] + tmpLLSeq + [tmpFinalPad], AWFLibrary[tmpChanName], channelInfo[tmpChanName].gateBuffer, channelInfo[tmpChanName].gateMinWidth))                                            
                    needZeroWF[tmpName][channelInfo[tmpChanName].gateChannel] = False
                    
                    seqLength[tmpName] = hardwareLLs[tmpName][channelInfo[tmpChanName].gateChannel][-1].size
                        
                elif tmpName[:6] == 'BBNAPS':
                    paddedLLs = []
                    tmpInitPad = create_padding_LL()
                    tmpFinalPad = create_padding_LL()
                    tmpInitPad.length = round(AWGFreq*(maxBackwardShift + channelInfo[tmpChanName].channelShift))                    
                    tmpFinalPad.length = round(AWGFreq*(maxForwardShift - channelInfo[tmpChanName].channelShift))                     
                    paddedLLs.append(tmpInitPad+tmpLLSeq+tmpFinalPad)

                    #TODO: Deal with APS marker channels
                    tmpInitPad.length = round(AWGFreq*(maxBackwardShift + channelInfo[tmpChanName].gateChannelShift))                    
                    tmpFinalPad.length = round(AWGFreq*(maxForwardShift - channelInfo[tmpChanName].gateChannelShift))                     
                    hardwareLLs[tmpName][channelInfo[tmpChanName].gateChannel].append(create_Tek_gate_seq(tmpInitPad + tmpLLSeq + tmpFinalPad, AWFLibrary[tmpChanName], channelInfo[tmpChanName].gateBuffer, channelInfo[tmpChanName].gateMinWidth))                                            
                    needZeroWF[tmpName][channelInfo[tmpChanName].gateChannel] = False
                       
                    hardwareLLs[tmpName][channelInfo[tmpChanName].IChannel]['LLs'].append(paddedLLs)
                    hardwareLLs[tmpName][channelInfo[tmpChanName].IChannel]['WFLibrary'] = IWFLibrary[tmpChanName]
                    needZeroWF[tmpName][channelInfo[tmpChanName].IChannel] = False
                   
                    hardwareLLs[tmpName][channelInfo[tmpChanName].QChannel]['LLs'].append(paddedLLs)
                    hardwareLLs[tmpName][channelInfo[tmpChanName].QChannel]['WFLibrary'] = QWFLibrary[tmpChanName]
                    needZeroWF[tmpName][channelInfo[tmpChanName].QChannel] = False
                    
            
            #Marker channel require only a single channel
            #TODO: Deal with APS marker channels            
            elif tmpChanType == Channels.ChannelTypes.marker:
                tmpInitPad = create_padding_LL()
                tmpFinalPad = create_padding_LL()
                tmpInitPad.length = round(AWGFreq*(maxBackwardShift + channelInfo[tmpChanName].channelShift))                    
                tmpFinalPad.length = round(AWGFreq*(maxForwardShift - channelInfo[tmpChanName].channelShift))                     
                hardwareLLs[tmpName][channelInfo[tmpChanName].channel].append(LL2sequence([tmpInitPad] + tmpLLSeq + [tmpFinalPad], AWFLibrary[tmpChanName]) > 0)
                needZeroWF[tmpName][channelInfo[tmpChanName].channel] = False
                   
        #Fill out unused channels with zero WFs
        for instrument in channelInfo['AWGList']:
            if instrument[:6] == 'TekAWG':
                for tmpChanName in hardwareLLs[instrument].keys():
                    if needZeroWF[instrument][tmpChanName]:
                        dtype = np.bool if tmpChanName[-2] == 'm' else np.float64
                        hardwareLLs[instrument][tmpChanName].append(np.zeros(seqLength[instrument], dtype=dtype))
            elif instrument[:6] == 'BBNAPS':
                #Create a minimial mini LL
                zeroLL = create_padding_LL()
                zeroLL.length = 16
                hardwareLLs[instrument][tmpChanName]['LLs'].append([zeroLL, zeroLL, zeroLL])
                
    return hardwareLLs

def create_Tek_gate_seq(LL, WFLibrary, gateBuffer, gateMinWidth):
    '''
    Helper function to create gate on a marker channel.
    '''
    tmpSeq = LL2sequence(LL, WFLibrary)
    
    #Go high when we are pulsing
    gateSeq = tmpSeq > 0
    
    #Extend by the gateBuffer
    #Assume that we have pulses with zero pts around so that we have an even number of switch points
    #All odd points are rise and even points are falls    
    bufferPts = round(gateBuffer*AWGFreq)
    switchPts = np.diff(gateSeq).nonzero()[0]
    
    if switchPts.size > 0:
        assert switchPts[0] > bufferPts, 'Oops! You need more lead points to accomodate the gating buffer.'
        for tmpPt in switchPts[0::2]:
            gateSeq[tmpPt-bufferPts:tmpPt+1] = True
        
        for tmpPt in switchPts[1::2]:
            gateSeq[tmpPt:tmpPt+bufferPts] = True
            
    #Make sure the minimum spacing is greater than gateMinWidth
    switchPts = np.diff(gateSeq).nonzero()[0]
    minWidthPts = round(gateMinWidth*AWGFreq)
    if switchPts.size > 2:
        gateSpacing = np.diff(switchPts)
        for ct, tmpSpacing in enumerate(gateSpacing[1::2]):
            if tmpSpacing < minWidthPts:
                gateSeq[switchPts[2*ct+1]:switchPts[2*ct+2]+1] = True

    return gateSeq            
                
                    
def LL2sequence(LL, WFLibrary):
    '''
    Helper function for converting a LL to a single sequence array for plotting or Tektronix purposes.
    '''
    #Count up how much space we need
    numPts = 0
    for tmpLLElement in LL:
        numPts += tmpLLElement.length*tmpLLElement.repeat
    
    #Allocate the array
    outSeq = np.zeros(numPts,dtype=WFLibrary.values()[0].dtype)
    
    idx = 0
    for tmpLLElement in LL:
        if tmpLLElement.isZero:
            pass
        elif tmpLLElement.isTimeAmplitude:
            outSeq[idx:idx+tmpLLElement.length] = np.repeat(WFLibrary[tmpLLElement.key], tmpLLElement.repeat)
        else:
            outSeq[idx:idx+tmpLLElement.length] = np.repeat(WFLibrary[tmpLLElement.key], tmpLLElement.repeat)
        idx += tmpLLElement.length*tmpLLElement.repeat
    
    return outSeq    
    
def compile_sequences(pulseSeqs):
    WFLibrary = {}
    pulseSeqLLs = [compile_sequence(pulseSeq, WFLibrary, AWGFreq)[0] for pulseSeq in pulseSeqs]

    return pulseSeqLLs, WFLibrary        

if __name__ == '__main__':
    
#    #Load the channel information from file
#    channelInfo = loadChannelInfo('channelInfo.dat', 'q1')
#    
#    q1 = channelInfo.channels['q1']
#    q2 = channelInfo.channels['q2']
    
    #Create a qubit channel
    q1 = Channels.QubitChannel(name='q1', piAmp=1.0, pi2Amp=0.5, pulseType='drag', pulseLength=40e-9, bufferTime= 2e-9, dragScaling=1)
    q2 = Channels.QubitChannel(name='q2', piAmp=1.0, pi2Amp=0.5, pulseType='drag', pulseLength=80e-9, bufferTime= 2e-9, dragScaling=1)

    measChannel = Channels.LogicalMarkerChannel(name='measChannel')
    digitizerTrig = Channels.LogicalMarkerChannel(name='digitizerTrig')

    channelInfo = {}
    channelInfo['q1'] = Channels.QuadratureChannel(AWGName='TekAWG1', IChannel='ch1', QChannel='ch2', gateChannel='ch1m1', channelShift=0e-9, gateBuffer=20e-9, gateMinWidth=100e-9)
    channelInfo['q2'] = Channels.QuadratureChannel(AWGName='TekAWG1', IChannel='ch3', QChannel='ch4', gateChannel='ch2m1', channelShift=0e-9, gateBuffer=20e-9, gateMinWidth=100e-9)
    channelInfo['measChannel'] = Channels.PhysicalMarkerChannel(AWGName='TekAWG1', channel='ch3m1' )
    channelInfo['digitizerTrig'] = Channels.PhysicalMarkerChannel(AWGName='TekAWG1', channel='ch4m1', channelShift=-100e-9 )

    channelInfo['AWGList'] = ['TekAWG1']
    
    #Define a typical sequence: say Pi Ramsey
    readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(2e-6)
    def single_ramsey_sequence(pulseSpacing):
        tmpSeq = [q1.X90(), q1.QId(pulseSpacing)+q2.X180(), q1.X90(), readoutBlock]
        tmpSeq[1].alignment = 'centre'
        return tmpSeq
        
    pulseSeqs = [single_ramsey_sequence(pulseSpacing) for pulseSpacing in np.linspace(1e-6,20e-6,100)]

#    pulseSeq = single_ramsey_sequence(100e-9)
#    LLs, WFLibrary = compile_sequence(pulseSeq, {}, AWGFreq)
#    AWGWFs = logical2hardware([LLs], WFLibrary, channelInfo)

    LLs, WFLibrary = compile_sequences(pulseSeqs)  
    
    AWGWFs = logical2hardware(LLs, WFLibrary, channelInfo)
    
    
    print('Writing Tek File...')
    write_Tek_file(AWGWFs['TekAWG1'], 'silly.awg', 'silly')
    print('Done writing Tek File.')

    plot_pulse_seqs(AWGWFs)
