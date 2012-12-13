'''
Created on Jan 8, 2012

Main classes for compiling pulse sequences.

@author: cryan
'''

from copy import copy
# from copy import deepcopy

import numpy as np
import matplotlib.pyplot as plt

# from Channels import Qubit
# from PulsePrimitives import *
# import PulseSequencePlotter

class Pulse(object):
    '''
    A single channel pulse object
        label - name of the pulse
        qubits - array of qubit/channel objects the pulse acts upon
        shape - numpy array pulse shape
        frameChange - accumulated phase from the pulse
    '''
    def __init__(self, label, qubits, shape, frameChange):
        self.label = label
        self.qubits = qubits
        self.shape = shape
        self.frameChange = frameChange

    # adding pulses concatenates the pulse shapes
    def __add__(self, other):
        newLabel = self.label+"+"+other.label
        if self.qubits != other.qubits:
            raise NameError("Can only concatenate pulses acting on the same channel")
        return Pulse(newLabel, self.qubits, np.append(self.shape, other.shape), self.frameChange + other.frameChange)

    # unary negation inverts the pulse shape
    # TODO: does the frame change need to be updated??
    def __neg__(self):
        return Pulse(self.label, self.qubits, -self.shape, self.frameChange)

    def __mul__(self, other):
        return self.promote()*other.promote()

    def promote(self):
        # promote a Pulse to a PulseBlock
        pb =  PulseBlock()
        pb.pulses = {self.qubits: self.shape}
        pb.channels = [self.qubits]
        return pb

class PulseBlock(object):
    '''
    The basic building block for pulse sequences. This is what we can concatenate together to make sequences.
    We overload the * operator so that we can combine pulse blocks on different channels.
    We overload the + operator to concatenate pulses on the same channel.
    '''
    def __init__(self):
        #Set some default values
        #How multiple channels are aligned.
        self.alignment = 'left'
        self.pulses = {}
        self.channels = []

    #Overload the multiplication operator to combine pulse blocks
    def __mul__(self, rhs):
        # make sure RHS is a PulseBlock
        rhs = rhs.promote()
        # we to go one layer deep in the copy so that we can manipulate self.pulses and self.channels w/o affecting the original object
        # should bundle this behavior into a __copy__ method
        result = copy(self)
        result.pulses = copy(self.pulses)
        result.channels = copy(self.channels)
        
        for (k, v) in rhs.pulses.items():
            if k in result.pulses.keys():
                raise NameError("Attempted to multiply pulses acting on the same space")
            else:
                result.pulses[k] = v
        result.channels += rhs.channels
        return result

    #PulseBlocks don't need to be promoted, so just return self
    def promote(self):
        return self

    #A list of the channels used in this block
    @property
    def channelNames(self):
        return [channel.name for channel in self.channels]

    #The maximum number of points needed for any channel on this block
    @property
    def maxPts(self):
        return max( [len(p.generateShape(AWGFreq)) for p in self.pulses.values()] )
        # return max( map(len, self.pulses.values()) )

class PulseSequence(object):
    '''
    A collection of pulse blocks which forms a sequence.
    '''

AWGFreq = 1e9

def show(seq):
    # normalize sequence to PulseBlocks
    seq = [p.promote() for p in seq]
    # find set of used channels
    qubits = set([])
    for step in seq:
        qubits |= set(step.pulses.keys())

    # initialize empty arrays for each qubit
    concatShapes = {q: np.array([], dtype=np.complex128) for q in qubits}

    # now loop through steps and push on the pulse shape, or an Id operation if none specified
    for step in seq:
        stepLength = step.maxPts
        for q in qubits:
            if q in step.pulses.keys():
                concatShapes[q] = np.append(concatShapes[q], step.pulses[q].generatePattern(AWGFreq))
            else:
                concatShapes[q] = np.append(concatShapes[q], np.zeros(stepLength))
    
    # plot
    for (ct,q) in enumerate(qubits):
        plt.subplot(len(qubits),1,ct+1)
        waveformToPlot = concatShapes[q]
        p = plt.plot(np.linspace(0,len(waveformToPlot)/AWGFreq,len(waveformToPlot)), np.real(waveformToPlot), 'r')
        p = plt.plot(np.linspace(0,len(waveformToPlot)/AWGFreq,len(waveformToPlot)), np.imag(waveformToPlot), 'b')
        plt.ylim((-1.05,1.05))
    plt.show(p)

def unitTest1():
    from Channels import Qubit
    from PulsePrimitives import X90, Id
    # eventually want q1 = Qubit('q1')
    q1 = Qubit('q1', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
    ramsey = [[X90(q1), Id(q1, delay), X90(q1)] for delay in np.linspace(0.0, 1e-6, 11)]
    # ramsey = [[X90(q1), Id(q1, delay), X90(q1), MEAS(q1)] for delay in np.linspace(0.0, 1e-6, 11)]
    show(ramsey[2])
    #compileSeq(ramsey)

def unitTest2():
    from Channels import Qubit
    from PulsePrimitives import X90, X, Xm, Y, CNOT
    q1 = Qubit('q1', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
    # goal is to make this just: q1 = Qubit('q1')
    q2 = Qubit('q2', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
    # seq = [X90(q1), X(q1)*Y(q2), CNOT(q1,q2), X(q2)+Xm(q2), Y(q1)*(X(q2)+Xm(q2)), MEAS(q1,q2)]
    seq = [X90(q1), X(q1)*Y(q2), CNOT(q1,q2), Xm(q2), Y(q1)*X(q2)]
    show(seq)
    #compileSeq(seq)

if __name__ == '__main__':
    unitTest1()
    unitTest2()

    #Create a qubit channel
    # channelObjs, channelDicts = Channels.load_channel_info('ChannelParams.json') 
    # 
    # #Pull out some short references
    # q1 = channelObjs['q1']
    # q2 = channelObjs['q2']
    # digitizerTrig = channelObjs['digitizerTrig']
    # measChannel = channelObjs['measChannel']
    # 
    # channelDicts['AWGList'] = ['TekAWG1', 'BBNAPS1']
    # 
    # #Define a typical sequence: say Pi Ramsey
    # readoutBlock = gatePulse(digitizerTrig, 100e-9)*gatePulse(measChannel, 2e-6)
    # def single_ramsey_sequence(pulseSpacing):
    #     tmpSeq = [X90p(q1), Xp(q2), X90p(q1), readoutBlock]
    #     tmpSeq[1].alignment = 'centre'
    #     return tmpSeq
    #     
    # pulseSeqs = [single_ramsey_sequence(pulseSpacing) for pulseSpacing in np.linspace(1e-6,20e-6,100)]
    # 
    # #Complile and write to file
    # AWGWFs, _LLs, _WFLibrary = compile_sequences(pulseSeqs, channelDicts, 'silly', 'silly') 
    # 
    # PulseSequencePlotter.plot_pulse_seqs(AWGWFs)
