import unittest

from QGL import *
from QGL.ControlFlow import CmpEq, CmpNeq, Goto, Call, Return
from QGL.BlockLabel import label, endlabel


class ControlFlow(unittest.TestCase):
    def setUp(self):
        self.q1 = Qubit(name='q1')
        self.q2 = Qubit(name='q2')

    def test_qif(self):
        q1 = self.q1
        seq1 = [X90(q1), Y90(q1)]
        seq2 = [X(q1), Y(q1), Z(q1)]
        label(seq1)
        label(seq2)
        # print qif(0, seq1, seq2)
        # print ([CmpEq(0), Goto(label(seq1))] + seq2, seq1 + [Goto(endlabel(seq2))])
        assert( qif(0, seq1, seq2) == [CmpEq(0), Goto(label(seq1)), (seq2, seq1 + [ Goto(endlabel(seq2)) ])] )

    def test_qwhile(self):
        q1 = self.q1
        seq1 = [X90(q1), Y90(q1)]
        label(seq1)
        # print qwhile(0, seq1)
        # print [CmpNeq(0), Goto(endlabel(seq1))] + seq1
        assert( qwhile(0, seq1) == [CmpNeq(0), Goto(endlabel(seq1))] + seq1 )

    def test_qdowhile(self):
        q1 = self.q1
        seq1 = [X90(q1), Y90(q1)]
        label(seq1)
        # print qdowhile(0, seq1)
        # print seq1 + [CmpEq(0), Goto(label(seq1))]
        assert( qdowhile(0, seq1) == seq1 + [CmpEq(0), Goto(label(seq1))] )

    def test_qcall(self):
        q1 = self.q1
        @qfunction
        def Reset(q):
            return qwhile(1, [X(q)])

        crseq = Reset(q1)
        seq1 = [Call(label(crseq[1]))]
        # print seq1
        subseq2 = crseq[1][2:-1]
        seq2 = [CmpNeq(1), Goto(endlabel(subseq2))] + subseq2 + [Return()]
        seq2[0].label = crseq[1][0].label
        # print seq2
        assert( Reset(q1) == (seq1, seq2) )

    def test_flatten_and_separate(self):
        seq = [1, ([2, ([3], [4, ([5, 6, 7], [8, 9])])], [10, 11])]
        main, branch = Compiler.flatten_and_separate(seq)
        assert( main == [1,2,3] )
        assert( branch == [4,5,6,7,8,9,10,11] )

    def test_compile(self):
        q1 = self.q1
        seq1 = [X90(q1), Y90(q1)]
        seq2 = [X(q1), Y(q1), Z(q1)]
        label(seq1)
        label(seq2)
        nseq = Compiler.normalize(seq1 + seq2)
        mainLL, branchLL, wfs1 = Compiler.compile_control_flow_sequence(nseq)
        # mainLL, branchLL, wfs2 = Compiler.compile_control_flow_sequence([X(q1), qif(0, seq1), Y(q1)])
        # assert(wfs1 == wfs2)
        # mainLL, branchLL, wfs3 = Compiler.compile_control_flow_sequence([X(q1), qif(0, seq1, seq2), Y(q1)])
        # assert(wfs1 == wfs3)


if __name__ == "__main__":
    
    unittest.main()
