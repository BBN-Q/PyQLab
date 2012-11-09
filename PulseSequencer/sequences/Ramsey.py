'''
Simple Ramsey experiment X90-delay-U90
'''

#Imports necessary for compiling sequences
from Channels import load_channel_info
from PulseSequencer import compile_sequences
from PulseSequencePlotter import plot_pulse_seqs

import numpy as np

def Ramsey(targetQubit = 'q1', fileName='Ramsey', pulseSpacings=np.linspace(100e-9,10e-6,100), freqTPPI=0, plotSeqs=True, readoutPulseLength=6e-6, AWGList=['TekAWG1','TekAWG2']):

    #Load the channel information
    channelObjs, channelDicts = load_channel_info('ChannelParams.json') 
    channelDicts['AWGList'] = AWGList
    
    #Assign the channels
    targetQ = channelObjs[targetQubit]
    digitizerTrig = channelObjs['digitizerTrig']
    measChannel = channelObjs['measChannel']
    
    #Define a single sequence
    readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(readoutPulseLength)
    def single_ramsey_sequence(pulseSpacing):
        tmpSeq = [targetQ.X90p(), targetQ.QId(pulseLength=pulseSpacing), targetQ.U90(phase=pulseSpacing*freqTPPI), readoutBlock]
        return tmpSeq
    
    #Create the list of pulse sequences
    pulseSeqs = [single_ramsey_sequence(pulseSpacing) for pulseSpacing in pulseSpacings]
    
    #Complile and write to file
    AWGWFs, _LLs, _WFLibrary = compile_sequences(pulseSeqs, channelDicts, fileName, 'Ramsey')
    
    #If asked then call the plot GUI
    if plotSeqs:
        plotterWin = plot_pulse_seqs(AWGWFs)
        return plotterWin

if __name__ == '__main__':
    plotWin = Ramsey()
