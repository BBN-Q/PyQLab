import unittest
import numpy as np

from QGL import *
from QGL.BlockLabel import label

class APSPatternUtils(unittest.TestCase):
    def setUp(self):
        # self.q1gate = Channels.LogicalMarkerChannel(label='q1-gate')
        # self.q1 = Qubit(label='q1', gateChan=self.q1gate)
        self.q1 = Qubit(label='q1')
        self.q1.pulseParams['length'] = 30e-9

        Compiler.channelLib = {'q1': self.q1}

    def test_unroll_loops_simple(self):
        q1 = self.q1
        seqs = [qrepeat(2, [qwait(), X(q1), Id(q1)]), qrepeat(2, [qwait(), Y(q1), Id(q1)])]
        a, b = APSPattern.unroll_loops(seqs)
        assert(a == seqs)
        assert(b == 2)

    def test_unroll_loops(self):
        q1 = self.q1
        seqs = [qrepeat(2, [qwait(), X(q1), Id(q1)]), qrepeat(3, [qwait(), Y(q1), Id(q1)])]
        a, b = APSPattern.unroll_loops(seqs)

        seqUnrolled = [qwait(), X(q1), Id(q1)]*2
        assert(a[0] == seqUnrolled)

        seqUnrolled = [qwait(), Y(q1), Id(q1)]*3
        assert(a[1] == seqUnrolled)

        assert(b == 0)

    def test_unroll_nested_loops(self):
        q1 = self.q1
        seqs = [qrepeat(2, [X(q1),Y(q1)] + qrepeat(3, [Z(q1)]) + [Y(q1),X(q1)]), [X(q1), Y(q1)]]
        a, b = APSPattern.unroll_loops(seqs)

        seqUnrolled = ([X(q1).promote(),Y(q1)] + [Z(q1).promote()]*3 + [Y(q1),X(q1)])*2

        assert(a[0] == seqUnrolled)

        assert(b == 0)

if __name__ == "__main__":    
    unittest.main()
