'''
Created on Jan 8, 2012

Main classes for compiling pulse sequences.

@author: cryan
'''

from copy import deepcopy

import numpy as np

import Channels

AWGFreq = 1.2e9

from TekPattern import write_Tek_file
from APSPattern import write_APS_file
import PulseSequencePlotter

import hashlib

#Some constants
ADDRESS_UNIT = 4 #everything is done in units of 4 timesteps
MIN_LL_ENTRY_COUNT = 3 #minimum length of mini link list
MIN_LL_COUNT = 4 #minimum number of address units in a LL entry
MIN_ENTRY_LENGTH = ADDRESS_UNIT*MIN_LL_COUNT
TAZKey = 0

#Minimum number of points fo r 

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
            self.pulses[channel.name].append(pulse)
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
        self.isTimeAmp = False
        self.hasTrigger = False
        self.triggerDelay = 0
        self.linkListRepeat = 0

def create_padding_LL():
    tmpLL = LLElement()
    tmpLL.isTimeAmp = True
    tmpLL.key = TAZKey
    return tmpLL
    
    
def compile_sequence(pulseSeq, WFLibrary = {}, AWGFreq = 1.2e9):
    '''
    Main function to compile a pulse sequence.
    This is where all the hard work is.  
    
    This is largely built around the APS model of waveforms and linklist specifying the sequence.
    However, it translates just fine to Tektronix too using the LL2Sequence helper function. 
    '''
    
    #Sort out which channels we have to deal with and initialize the waveforms
    logicalLLs = {}
    for tmpBlock in pulseSeq:
        for tmpChan in tmpBlock.channels:
            if tmpChan.name not in logicalLLs:
                logicalLLs[tmpChan.name] = []
            if tmpChan.name not in WFLibrary:
                WFLibrary[tmpChan.name] = {}
                #Add the TAZ key to the WFLibrary by default
                WFLibrary[tmpChan.name][TAZKey] = np.zeros(1, dtype=np.complex)
    emptyLLs = deepcopy(logicalLLs)

    #Loop over each of the pulse sequence blocks
    #Generate the shapes and build the waveform library
    #Then parse the paddings according to the alignment
    for tmpBlock in pulseSeq:
        tmpLLs = deepcopy(emptyLLs)
        
        #Loop over each channel in the block and add LL elements
        for tmpChanName in tmpBlock.channelNames:
            for tmpPulse in tmpBlock.pulses[tmpChanName]:
                tmpLLElement = LLElement()
                if id(tmpPulse) not in WFLibrary[tmpChanName]:
                    WFLibrary[tmpChanName][id(tmpPulse)] = tmpPulse.generatePattern(AWGFreq)
                tmpLLElement.key = id(tmpPulse)
                tmpLLElement.isTimeAmp = tmpPulse.isTimeAmp
                tmpLLElement.length = tmpPulse.numPoints(AWGFreq)
                tmpLLs[tmpChanName].append(tmpLLElement)
            
        #Now adjust the paddings according the pulse block alignment
        for k, miniLL in tmpLLs.items():
            numPts = 0
            for tmpElement in miniLL:
                numPts += tmpElement.length
            padLength = tmpBlock.maxPts-numPts
            if padLength > 0:
                if tmpBlock.alignment == 'left':
                    #We pad the final LL element
                    tmpLLs[k].append(create_padding_LL())
                    tmpLLs[k][-1].length = padLength
                elif tmpBlock.alignment == 'right':
                    #We pad the first LL element
                    tmpLLs[k].insert(0, create_padding_LL())
                    tmpLLs[k][0].length = padLength
                elif tmpBlock.alignment == 'centre':
                    #We split the difference
                    tmpLLs[k].insert(0, create_padding_LL())
                    tmpLLs[k][0].length = padLength//2
                    tmpLLs[k].append(create_padding_LL())
                    tmpLLs[k][-1].length = padLength//2 + 1 if padLength%2 else padLength//2
        
        #Append this block onto the total pulse sequence
        for tmpName in logicalLLs.keys():
            logicalLLs[tmpName] += tmpLLs[tmpName]
        
    return logicalLLs, WFLibrary


def TekChannels():
    '''
    The set of empty channels for a Tektronix AWG
    '''
    return {'ch1':[], 'ch2':[], 'ch3':[], 'ch4':[], 'ch1m1':[], 'ch1m2':[], 'ch2m1':[], 'ch2m2':[], 'ch3m1':[], 'ch3m2':[] , 'ch4m1':[], 'ch4m2':[]}

def APSChannels():
    '''
    The set of empty channels for a BBN APS.
    '''
    return {chanStr:{'LLs':[], 'WFLibrary':{0:np.zeros(1)}} for chanStr in  ['ch1','ch2','ch3','ch4']}
        
def APS_preprocess(miniLL, IWFLibrary, QWFLibrary):
    '''
    Helper function to deal with LL elements less than minimum LL entry count
    '''
    #Find the problem entries and fix
    newMiniLL = []
    entryct = 0
    while entryct < len(miniLL)-1:
        curEntry = miniLL[0]
        if curEntry.length > MIN_ENTRY_LENGTH:
            newMiniLL.append(curEntry)
            entryct += 1
        else:
            nextEntry = miniLL[entryct+1]
            #See if the next entry is a WF we can append too
            #TODO: Handle repeats properly
            if curEntry.isTimeAmp and not nextEntry.isTimeAmp:
                #Concatenate the waveforms                
                IpaddedWF = np.hstack((IWFLibrary[curEntry.key]*np.ones(curEntry.length//ADDRESS_UNIT), IWFLibrary[nextEntry.key]))
                #Hash the result to generate a new unique key and add
                newKey = hashlib.sha1(IpaddedWF.view(np.uint8)).hexdigest()
                IWFLibrary[newKey] = IpaddedWF
                QWFLibrary[newKey] = np.hstack((IWFLibrary[curEntry.key]*np.ones(curEntry.length//ADDRESS_UNIT), IWFLibrary[nextEntry.key]))
                nextEntry.key = newKey
                nextEntry.length = IWFLibrary[newKey].size
                newMiniLL.append(nextEntry)
                entryct += 2
        
def logical2hardware(pulseSeqs, WFLibrary, channelInfo):

    '''
    Final compiling steps which translates from logical channels to physical channels and adding gating pulses.
    '''
    #For each of the instruments create the zero channels
    hardwareLLs = {}
    for instrument in channelInfo['AWGList']:
        if instrument[:6] == 'TekAWG':
            hardwareLLs[instrument] = TekChannels()
            
        elif instrument[:6] == 'BBNAPS':
            hardwareLLs[instrument] = APSChannels()
            
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
        if channelInfo[tmpChanName]['channelType'] == 'quadratureMod':
            tmpT = channelInfo[channelInfo[tmpChanName]['physicalChannel']]['correctionT']
        else:
            tmpT = [[1,0],[0,1]]
        for tmpKey, tmpWF in WFLibrary[tmpChanName].items():
            IWFLibrary[tmpChanName][tmpKey] = tmpWF.real*tmpT[0][0] + tmpWF.imag*tmpT[0][1]
            QWFLibrary[tmpChanName][tmpKey] = tmpWF.imag*tmpT[1][1]
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
        
        for tmpChanName in logicalLLs.keys():
            #Deal with the different channeltypes
            tmpChanType = channelInfo[tmpChanName]['channelType']
            tmpPhysChan = channelInfo[channelInfo[tmpChanName]['physicalChannel']]
    
            if tmpChanType == 'quadratureMod':
                tmpCarrier = channelInfo[tmpPhysChan['carrierGen']]
                tmpGateChannel = channelInfo[tmpCarrier['gateChannel']]
                
                if tmpPhysChan['channelShift'] > 0:
                    maxForwardShift = max(maxForwardShift, tmpPhysChan['channelShift'])
                else:
                    maxBackwardShift = max(maxBackwardShift, -tmpPhysChan['channelShift'])
                tmpShift = tmpCarrier['gateChannelShift'] + tmpGateChannel['channelShift']
                if tmpShift > 0:
                    maxForwardShift = max(maxForwardShift, tmpShift)
                else:
                    maxBackwardShift = max(maxBackwardShift, -tmpShift)
                
            elif tmpChanType == 'marker':
                if tmpPhysChan['channelShift'] > 0:
                    maxForwardShift = max(maxForwardShift, tmpPhysChan['channelShift'])
                else:
                    maxBackwardShift = max(maxBackwardShift, -tmpPhysChan['channelShift'])
        
        #Add a safety buffer for gate buffers and whatnot
        maxBackwardShift += 100e-9
        maxForwardShift += 100e-9
       
        #Loop through each of the logical channels and assign the LL to the appropriate 
        for tmpChanName, tmpLLSeq in logicalLLs.items():
            #Deal with the different channeltypes
            tmpChanType = channelInfo[tmpChanName]['channelType']
            tmpPhysChan = channelInfo[channelInfo[tmpChanName]['physicalChannel']]
            tmpAWGName = tmpPhysChan['AWGName']

            #Quadrature channels require two analog channels        
            if tmpChanType == 'quadratureMod':
                #Switch on the type of AWG
                tmpCarrier = channelInfo[tmpPhysChan['carrierGen']]
                tmpGateChannel = channelInfo[tmpCarrier['gateChannel']]
                if tmpAWGName[:6] == 'TekAWG':
                    
                    tmpInitPad = create_padding_LL()
                    tmpFinalPad = create_padding_LL()

                    #I Channel
                    tmpInitPad.length = int(AWGFreq*(maxBackwardShift + tmpPhysChan['channelShift']))                    
                    tmpFinalPad.length = int(AWGFreq*(maxForwardShift - tmpPhysChan['channelShift']))                     
                    hardwareLLs[tmpAWGName][tmpPhysChan['IChannel']].append(LL2sequence([tmpInitPad] + tmpLLSeq + [tmpFinalPad], IWFLibrary[tmpChanName]))
                    needZeroWF[tmpAWGName][tmpPhysChan['IChannel']] = False
                    #Q Channel
                    hardwareLLs[tmpAWGName][tmpPhysChan['QChannel']].append(LL2sequence([tmpInitPad] + tmpLLSeq + [tmpFinalPad], QWFLibrary[tmpChanName]))
                    needZeroWF[tmpAWGName][tmpPhysChan['QChannel']] = False

                    #SSBFreq in normalized AWG timestep units
                    SSBFreq = 1e9*(channelInfo[tmpChanName]['frequency']-tmpCarrier['frequency'])/AWGFreq                    

                    if np.abs(SSBFreq) > 1e-12:
                        tmpWF = hardwareLLs[tmpAWGName][tmpPhysChan['IChannel']][-1] +1j*hardwareLLs[tmpAWGName][tmpPhysChan['IChannel']][-1]
                        SSBWF = tmpWF*np.exp(1j*2*np.pi*np.arange(tmpWF.size))
                        hardwareLLs[tmpAWGName][tmpPhysChan['IChannel']][-1] = SSBWF.real
                        hardwareLLs[tmpAWGName][tmpPhysChan['QChannel']][-1] = SSBWF.imag
                        

                elif tmpAWGName[:6] == 'BBNAPS':
                    tmpInitPad = create_padding_LL()
                    tmpFinalPad = create_padding_LL()
                    tmpInitPad.length = round(AWGFreq*(maxBackwardShift + tmpPhysChan['channelShift']))                    
                    tmpFinalPad.length = round(AWGFreq*(maxForwardShift - tmpPhysChan['channelShift']))                     
                    paddedLLs = [tmpInitPad]+tmpLLSeq+[tmpFinalPad] 
                    APS_preprocess(paddedLLs, IWFLibrary[tmpChanName], QWFLibrary[tmpChanName])

                    hardwareLLs[tmpAWGName][tmpPhysChan['IChannel']]['LLs'].append(paddedLLs)
                    hardwareLLs[tmpAWGName][tmpPhysChan['IChannel']]['WFLibrary'] = IWFLibrary[tmpChanName]
                    needZeroWF[tmpAWGName][tmpPhysChan['IChannel']] = False
                   
                    hardwareLLs[tmpAWGName][tmpPhysChan['QChannel']]['LLs'].append(paddedLLs)
                    hardwareLLs[tmpAWGName][tmpPhysChan['QChannel']]['WFLibrary'] = QWFLibrary[tmpChanName]
                    needZeroWF[tmpAWGName][tmpPhysChan['QChannel']] = False
                    
                else:
                    raise NameError('Unknown AWG Type: we currently only handle TekAWG and BBNAPS.')

                #Gate channel
                #TODO: Deal with APS marker channels
                tmpShift = tmpCarrier['gateChannelShift'] + tmpGateChannel['channelShift']
                tmpInitPad.length = round(AWGFreq*(maxBackwardShift + tmpShift))                    
                tmpFinalPad.length = round(AWGFreq*(maxForwardShift - tmpShift))
                #Multiple channels can map to the same marker (e.g. CR gates) so check if there is data and AND the two together if there is
                if needZeroWF[tmpGateChannel['AWGName']][tmpGateChannel['channel']]:
                    hardwareLLs[tmpGateChannel['AWGName']][tmpGateChannel['channel']].append(create_Tek_gate_seq([tmpInitPad] + tmpLLSeq + [tmpFinalPad], AWFLibrary[tmpChanName], tmpCarrier['gateBuffer'], tmpCarrier['gateMinWidth']))                                            
                    needZeroWF[tmpGateChannel['AWGName']][tmpGateChannel['channel']] = False
                else:
                    hardwareLLs[tmpGateChannel['AWGName']][tmpGateChannel['channel']] = np.logical_or(hardwareLLs[tmpGateChannel['AWGName']][tmpGateChannel['channel']] , create_Tek_gate_seq([tmpInitPad] + tmpLLSeq + [tmpFinalPad], AWFLibrary[tmpChanName], tmpCarrier['gateBuffer'], tmpCarrier['gateMinWidth']))
                
                #Set the sequence length for unused channels
                seqLength[tmpAWGName] = hardwareLLs[tmpGateChannel['AWGName']][tmpGateChannel['channel']][-1].size
                seqLength[tmpGateChannel['AWGName']] = hardwareLLs[tmpGateChannel['AWGName']][tmpGateChannel['channel']][-1].size

            #Marker channel require only a single channel
            #TODO: Deal with APS marker channels            
            elif tmpChanType == 'marker':
                tmpInitPad = create_padding_LL()
                tmpFinalPad = create_padding_LL()
                tmpInitPad.length = round(AWGFreq*(maxBackwardShift + tmpPhysChan['channelShift']))                    
                tmpFinalPad.length = round(AWGFreq*(maxForwardShift - tmpPhysChan['channelShift']))                     
                hardwareLLs[tmpAWGName][tmpPhysChan['channel']].append(LL2sequence([tmpInitPad] + tmpLLSeq + [tmpFinalPad], AWFLibrary[tmpChanName]) > 0)
                needZeroWF[tmpAWGName][tmpPhysChan['channel']] = False
                   
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
                for tmpChanName in hardwareLLs[instrument].keys():
                    if needZeroWF[instrument][tmpChanName]:
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
                
                    
def LL2sequence(miniLL, WFLibrary):
    '''
    Helper function for converting a LL to a single sequence array for plotting or Tektronix purposes.
    '''
    #Count up how much space we need
    numPts = 0
    for tmpLLElement in miniLL:
        numPts += tmpLLElement.length*tmpLLElement.repeat
    
    #Allocate the array
    tmpDtype = np.double if WFLibrary is None else WFLibrary.values()[0].dtype    
    outSeq = np.zeros(numPts,dtype=tmpDtype)
    
    idx = 0
    for tmpLLElement in miniLL:
        if tmpLLElement.isTimeAmp:
            outSeq[idx:idx+tmpLLElement.length] = WFLibrary[tmpLLElement.key]*np.ones(tmpLLElement.repeat)
        else:
            outSeq[idx:idx+tmpLLElement.length] = np.tile(WFLibrary[tmpLLElement.key], tmpLLElement.repeat)
        idx += tmpLLElement.length*tmpLLElement.repeat
    
    return outSeq    
    
def compile_sequences(pulseSeqs, channelDicts, fileName=None, seqName='NoName'):
    '''
    Helper function that combines several functions to completely compile and write to file a list of pulse sequences.
    '''
    print('Number of sequences: {0}'.format(len(pulseSeqs)))
    #First compile the sequences to LLs and WF libraries
    WFLibrary = {}
    LLs = [compile_sequence(pulseSeq, WFLibrary, AWGFreq)[0] for pulseSeq in pulseSeqs]

    #Compile LLs down to the hardware    
    AWGWFs = logical2hardware(LLs, WFLibrary, channelDicts)

    #If we have a filename then output the AWG files
    if fileName:
        for tmpAWG in channelDicts['AWGList']:
            if tmpAWG[0:6] == 'TekAWG':
                print('Writing Tek File for {0}...'.format(tmpAWG))
                #Ugly hardcoded hack, set ch4m1 for Labricks to 2V
                options = {'markerLevels': {'ch4m1': {'low':0.0, 'high':2.0}}}
                write_Tek_file(AWGWFs[tmpAWG], '{0}-{1}.awg'.format(fileName, tmpAWG) , seqName, options)
                print('Finished writing Tek file.')
            elif tmpAWG[0:6] == 'BBNAPS':
                print('Writing APS File for {0}...'.format(tmpAWG))
                write_APS_file(AWGWFs[tmpAWG], '{0}-{1}.h5'.format(fileName, tmpAWG))
                print('Finished writing APS file.')

    return AWGWFs, LLs, WFLibrary        

if __name__ == '__main__':
    
    #Create a qubit channel
    channelObjs, channelDicts = Channels.load_channel_info('ChannelParams.json') 
    
    #Pull out some short references
    q1 = channelObjs['q1']
    q2 = channelObjs['q2']
    digitizerTrig = channelObjs['digitizerTrig']
    measChannel = channelObjs['measChannel']
    
    channelDicts['AWGList'] = ['TekAWG1', 'BBNAPS1']
    
    #Define a typical sequence: say Pi Ramsey
    readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(2e-6)
    def single_ramsey_sequence(pulseSpacing):
        tmpSeq = [q1.X90p(), q2.Xp(), q1.X90p(), readoutBlock]
        tmpSeq[1].alignment = 'centre'
        return tmpSeq
        
    pulseSeqs = [single_ramsey_sequence(pulseSpacing) for pulseSpacing in np.linspace(1e-6,20e-6,100)]

#    pulseSeq = single_ramsey_sequence(100e-9)
#    LLs, WFLibrary = compile_sequence(pulseSeq, {}, AWGFreq)
#    AWGWFs = logical2hardware([LLs], WFLibrary, channelDicts)

    #Complile and write to file
    AWGWFs, _LLs, _WFLibrary = compile_sequences(pulseSeqs, channelDicts, 'silly', 'silly') 

    PulseSequencePlotter.plot_pulse_seqs(AWGWFs)
