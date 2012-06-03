'''
Simple variable amplitude Rabi experiment 
'''

#Imports necessary for compiling sequences
from Channels import load_channel_info
from PulseSequencer import compile_sequences
from PulseSequencePlotter import plot_pulse_seqs

import numpy as np

def RabiAmp(targetQubit = 'q1', fileName='Rabi', pulseAmps=np.linspace(-1,1,81), plotSeqs=True, readoutPulseLength=6.66e-6, AWGList=['TekAWG1','BBNAPS1']):

    #Load the channel information
    channelObjs, channelDicts = load_channel_info('ChannelParams.json') 
    channelDicts['AWGList'] = AWGList
    
    #Assign the channels
    targetQ = channelObjs[targetQubit]
    digitizerTrig = channelObjs['digitizerTrig']
    measChannel = channelObjs['measChannel']
    
    #Define a single sequence
    readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(readoutPulseLength)
    def single_rabi_sequence(pulseAmp):
        tmpSeq = [targetQ.Xtheta(amp=pulseAmp), readoutBlock]
        return tmpSeq
    
    #Create the list of pulse sequences
    pulseSeqs = [single_rabi_sequence(pulseAmp) for pulseAmp in pulseAmps]
    
    #Complile and write to file
    AWGWFs, _LLs, _WFLibrary = compile_sequences(pulseSeqs, channelDicts, fileName, 'Rabi')  
    
    #If asked then call the plot GUI
    if plotSeqs:
        plotterWin = plot_pulse_seqs(AWGWFs)
        return plotterWin

if __name__ == '__main__':
    plotWin = RabiAmp()