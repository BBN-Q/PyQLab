'''
Simple Ramsey experiment X90-delay-U90
'''

#Imports necessary for compiling sequences
from Channels import load_channel_info
from PulseSequencer import compile_sequences, logical2hardware
from PulseSequencePlotter import plot_pulse_seqs
from TekPattern import write_Tek_file
from APSPattern import write_APS_file

import numpy as np

def Ramsey(targetQubit = 'q1', fileName='Ramsey', pulseSpacings=np.linspace(0,10e-6,100), plotSeqs=True, readoutPulseLength=6e-6):

    #Load the channel information
    channelObjs, channelDicts = load_channel_info('ChannelParams.json') 
    
    #Assign the channels
    targetQ = channelObjs[targetQubit]
    digitizerTrig = channelObjs['digitizerTrig']
    measChannel = channelObjs['measChannel']
    
    channelDicts['AWGList'] = ['TekAWG1','BBNAPS1']
    
    #Define a typical sequence: say Pi Ramsey
    readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(readoutPulseLength)
    def single_ramsey_sequence(pulseSpacing):
        tmpSeq = [targetQ.X90(), targetQ.QId(pulseSpacing), targetQ.X90(), readoutBlock]
        return tmpSeq
    
    #Create the list of pulse sequences
    pulseSeqs = [single_ramsey_sequence(pulseSpacing) for pulseSpacing in pulseSpacings]
    
    #Complile to link lists
    LLs, WFLibrary = compile_sequences(pulseSeqs)  
    
    #Comile LLs down to the hardware    
    AWGWFs = logical2hardware(LLs, WFLibrary, channelDicts)
    
    #Write out the AWG files
    for tmpAWG in channelDicts['AWGList']:
        if tmpAWG[0:6] == 'TekAWG':
            print('Writing Tek File...')
            write_Tek_file(AWGWFs[tmpAWG], fileName+'.awg', 'Ramsey')
            print('Done writing Tek File.')
        elif tmpAWG[0:6] == 'BBNAPS':
            print('Writing APS File....')
            write_APS_file(AWGWFs[tmpAWG], fileName+'.h5')
    
    #If asked then call the plot GUI
    if plotSeqs:
        plot_pulse_seqs(AWGWFs)

