'''
Tune up the DRAG scaling parameter with a flip-flip sequence
'''

#Imports necessary for compiling sequences
from Channels import load_channel_info
from PulseSequencer import compile_sequences
from PulseSequencePlotter import plot_pulse_seqs

import numpy as np

def PiRabi(controlQubit = 'q1', CRChannel='CR', fileName='PiRabi', plotSeqs=True, readoutPulseLength=1.5e-6, AWGList=['TekAWG1','BBNAPS1']):
    '''
    A simple sequence to observe the CR effect with the difference in nutation frequency when the control is in
    the ground and excited states.'
    '''

    #Load the channel information
    channelObjs, channelDicts = load_channel_info('ChannelParams.json') 
    channelDicts['AWGList'] = AWGList
    
    #Assign the channels
    targetQ = channelObjs[controlQubit]
    CR = channelObjs[CRChannel]
    digitizerTrig = channelObjs['digitizerTrig']
    measChannel = channelObjs['measChannel']

    numSteps = 80
    stepSize = 3.333e-9
    minWidth = 100e-9
    CRpulseWidths = np.arange(minWidth, minWidth+numSteps*stepSize, stepSize)


    CRRise = CR.Utheta(pulseType='gaussOn', pulseLength=40e-9, amp=1)
    CRFall = CR.Utheta(pulseType='gaussOff', pulseLength=40e-9, amp=1)

    #Define a single sequence
    readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(readoutPulseLength)
    def single_PiRabi_sequence(pulseLength):
        tmpSeq = [targetQ.Xp(), CRRise, CR.Utheta(pulseType='square', pulseLength=pulseLength-80e-9, amp=1), CRFall, targetQ.Xp(), readoutBlock]
        return tmpSeq

    def single_NoPiRabi_sequence(pulseLengths):
        tmpSeq = [CRRise, CR.Utheta(pulseType='square', pulseLength=pulseLength-80e-9, amp=1), CRFall, readoutBlock]
        return tmpSeq

    
    pulseSeqs = [single_PiRabi_sequence(pulseLength) for pulseLength in CRpulseWidths] + \
                   [single_NoPiRabi_sequence(pulseLength) for pulseLength in CRpulseWidths]      
    
    #Complile and write to file
    AWGWFs, _LLs, _WFLibrary = compile_sequences(pulseSeqs, channelDicts, fileName, 'FlipFlop')  
    
    import cPickle
    with open('pulseSeq.pkl', 'wb') as FID:
        cPickle.dump(AWGWFs, FID)
    
    
    #If asked then call the plot GUI
    if plotSeqs:
        plotterWin = plot_pulse_seqs(AWGWFs)
        return plotterWin

if __name__ == '__main__':
    plotWin = PiRabi()