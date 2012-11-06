'''
Tune up the DRAG scaling parameter with a flip-flip sequence
'''

#Imports necessary for compiling sequences
from Channels import load_channel_info
from PulseSequencer import compile_sequences
from PulseSequencePlotter import plot_pulse_seqs

from copy import deepcopy
from itertools import chain
import numpy as np

def FlipFlop(targetQubit = 'q1', fileName='FlipFlop', dragScalings=np.linspace(-2,2,21), plotSeqs=True, readoutPulseLength=6.66e-6, AWGList=['TekAWG1','BBNAPS1']):

    #Load the channel information
    channelObjs, channelDicts = load_channel_info('ChannelParams.json') 
    channelDicts['AWGList'] = AWGList
    
    #Assign the channels
    targetQ = channelObjs[targetQubit]
    digitizerTrig = channelObjs['digitizerTrig']
    measChannel = channelObjs['measChannel']

    #Maximum number of flip-flops
    maxFFs = 7
    #Define a single sequence
    readoutBlock = digitizerTrig.gatePulse(100e-9)+measChannel.gatePulse(readoutPulseLength)
    def single_flipflop_sequence(dragScaling, numFFs):
        #Create a copy of the qubit channel
        tmpQ = deepcopy(targetQ)
        tmpQ.dragScaling = dragScaling
        baseFFSeq = [tmpQ.X90p(), tmpQ.X90m()]
        tmpSeq = [tmpQ.X90p()] + baseFFSeq*numFFs + [tmpQ.Y90p(), readoutBlock]
        return tmpSeq
    
    #Create the list of list of pulse sequences with an identity at the start for visual reference
    pulseSeqs = [[[targetQ.QId(), readoutBlock]] + [single_flipflop_sequence(dragScaling, numFFs) for numFFs in range(maxFFs)] for dragScaling in dragScalings]
    #Flatten the list
    pulseSeqs = list(chain.from_iterable(pulseSeqs))

    #Add a final pi for reference
    pulseSeqs.append([targetQ.Xp(), readoutBlock])
    
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
    plotWin = FlipFlop()