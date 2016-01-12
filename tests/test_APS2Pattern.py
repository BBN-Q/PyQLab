import h5py
import unittest
import numpy as np
from copy import copy

from QGL import *
from instruments.drivers import APS2Pattern
from test_Sequences import APS2Helper

class APSPatternUtils(unittest.TestCase, APS2Helper):
    def setUp(self):
        self.q1gate = Channels.LogicalMarkerChannel(label='q1-gate')
        self.q1 = Qubit(label='q1', gateChan=self.q1gate)
        self.q1 = Qubit(label='q1')
        self.q1.pulseParams['length'] = 30e-9

        Compiler.channelLib = {'q1': self.q1, 'q1-gate': self.q1gate}
        APS2Helper.__init__(self)
        APS2Helper.setUp(self)

    def test_synchronize_control_flow(self):
        q1 = self.q1

        pulse = Compiler.Waveform()
        pulse.length = 24
        pulse.key = 12345
        delay = Compiler.Waveform()
        delay.length = 100
        delay.isTimeAmp = True
        blank = Compiler.Waveform( BLANK(q1, pulse.length) )

        seq_1 = [qwait(), delay, copy(pulse), qwait(), copy(pulse)]
        seq_2 = [qwait(), copy(blank), qwait(), copy(blank)]
        offsets = { APS2Pattern.wf_sig(pulse) : 0 }
        
        instructions = APS2Pattern.create_seq_instructions([seq_1, seq_2, [], [], []], offsets)

        instr_types = [
            APS2Pattern.SYNC,
            APS2Pattern.WAIT,
            APS2Pattern.WFM,
            APS2Pattern.MARKER,
            APS2Pattern.WFM,
            APS2Pattern.WAIT,
            APS2Pattern.WFM,
            APS2Pattern.MARKER
        ]

        for actual, expected in zip(instructions, instr_types):
            instrOpCode = (actual.header >> 4) & 0xf
            assert(instrOpCode == expected)

    def test_propagate_phase(self):
        q = self.q1
        q.frequency = 10e6
        seq = qif(0,[Id(q), X(q)],[X(q), Id(q)])
        seq_out = self.partial_compile(seq)
        assert(seq_out[0][-3].phase == seq_out[0][-7].phase)
        seq = qif(0,[Id(q), X(q)]) + qif(1, [X(q), Id(q)])
        seq_out =  self.partial_compile(seq)
        assert(seq_out[0][-3].phase == seq_out[0][-8].phase)

    def partial_compile(self, seq):
        channels = set([])
        channels |= Compiler.find_unique_channels(seq)
        wireSeqs = Compiler.compile_sequences([seq], channels)
        physWires = Compiler.map_logical_to_physical(wireSeqs)
        wfs = Compiler.generate_waveforms(physWires)
        physWires = Compiler.pulses_to_waveforms(physWires)
        awgData = Compiler.bundle_wires(physWires, wfs)
        seq_out, wfLib = APS2Pattern.preprocess(awgData['APS1']['ch12']['linkList'], awgData['APS1']['ch12']['wfLib'], awgData['APS1']['ch12']['correctionT'])
        return seq_out

if __name__ == "__main__":    
    unittest.main()
