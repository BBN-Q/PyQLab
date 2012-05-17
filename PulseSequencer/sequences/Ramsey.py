# Simple Ramsey experiment X90-delay-U90

from Channels import load_channel_info
from PulseSequencer import compile_sequences, logical2hardware
from PulseSequencePlotter import plot_pulse_seqs
from TekPattern import write_Tek_file

import numpy as np

#Channel boiler-plate

#Load the channel information
channelObjs, channelDicts = load_channel_info('ChannelParams.json') 

q1 = channelObjs['q1']
q2 = channelObjs['q2']
digitizerTrig = channelObjs['digitizerTrig']
measChannel = channelObjs['measChannel']

channelDicts['AWGList'] = ['TekAWG1']


#Define a typical sequence: say Pi Ramsey
readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(2e-6)
def single_ramsey_sequence(pulseSpacing):
    tmpSeq = [q1.X90(), q1.QId(pulseSpacing)+q2.X180(), q1.X90(), readoutBlock]
    tmpSeq[1].alignment = 'centre'
    return tmpSeq

pulseSeqs = [single_ramsey_sequence(pulseSpacing) for pulseSpacing in np.linspace(1e-6,20e-6,100)]

LLs, WFLibrary = compile_sequences(pulseSeqs)  
    
AWGWFs = logical2hardware(LLs, WFLibrary, channelDicts)


print('Writing Tek File...')
write_Tek_file(AWGWFs['TekAWG1'], 'silly.awg', 'silly')
print('Done writing Tek File.')

plot_pulse_seqs(AWGWFs)


