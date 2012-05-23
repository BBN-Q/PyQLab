'''
Simple Ramsey experiment X90-delay-U90
'''

#Imports necessary for compiling sequences
from Channels import load_channel_info
from PulseSequencer import compile_sequences, logical2hardware
from PulseSequencePlotter import plot_pulse_seqs
from TekPattern import write_Tek_file

import numpy as np


def Ramsey(targetQubit = 'q1', fileName='Ramsey', pulseSpacings=np.linspace(0,10e-6,100), plotSeqs=True, readoutPulseLength=6e-6):

    #Channel boiler-plate
    #Load the channel information
    channelObjs, channelDicts = load_channel_info('ChannelParams.json') 
    
    targetQ = channelObjs[targetQubit]
    digitizerTrig = channelObjs['digitizerTrig']
    measChannel = channelObjs['measChannel']
    
    channelDicts['AWGList'] = ['TekAWG1']
    
    #Define a typical sequence: say Pi Ramsey
    readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(readoutPulseLength)
    def single_ramsey_sequence(pulseSpacing):
        tmpSeq = [targetQ.X90(), targetQ.QId(pulseSpacing), targetQ.X90(), readoutBlock]
        tmpSeq[1].alignment = 'centre'
        return tmpSeq
    
    #Create the list of pulse sequences
    pulseSeqs = [single_ramsey_sequence(pulseSpacing) for pulseSpacing in pulseSpacings]
    
    #Complile to link lists
    LLs, WFLibrary = compile_sequences(pulseSeqs)  
        
    AWGWFs = logical2hardware(LLs, WFLibrary, channelDicts)
    
    print('Writing Tek File...')
    write_Tek_file(AWGWFs['TekAWG1'], 'silly.awg', 'silly')
    print('Done writing Tek File.')
    
    if plotSeqs:
        plot_pulse_seqs(AWGWFs)

