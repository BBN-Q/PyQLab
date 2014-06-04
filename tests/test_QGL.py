import unittest
import numpy as np


from QGL import *


class SingleQubit(unittest.TestCase):
    def setUp(self):
        self.q1 = Qubit(label='q1')
        self.q1.pulseParams['length'] = 30e-9

    def test_Ramsey(self):
        '''
        Test simple Ramsey sequence
        '''
        q1 = self.q1
        ramsey = [[X90(q1), Id(q1, delay), X90(q1)] for delay in np.linspace(0.0, 1e-6, 11)]
        show(ramsey[2])
        return ramsey

    def test_repeat(self):
        q1 = self.q1
        seq = [X90(q1), repeat(Y(q1), 5), X90(q1)]
        show(seq)
        return seq
    
    def test_compile(self):
        seqs = self.test_Ramsey()
        LL, wfLib = Compiler.compile_sequences([Compiler.normalize(s) for s in seqs])
        assert(len(LL[self.q1]) == 11)
        assert(len(LL[self.q1][0]) == 2)
        assert( all([len(miniLL) == 3 for miniLL in LL[self.q1][1:]]) )
        assert(len(wfLib[self.q1]) == 2) # just X90 + TAZ

class MultiQubit(unittest.TestCase):
    def setUp(self):
        self.q1 = Qubit(label='q1')
        self.q1.pulseParams['length'] = 30e-9
        self.q2 = Qubit(label='q2')
        self.q2.pulseParams['length'] = 30e-9

    def test_Operators(self):
        q1 = self.q1
        q2 = self.q2
        # seq = [X90(q1), X(q1)*Y(q2), CNOT(q1,q2), X(q2)+Xm(q2), Y(q1)*(X(q2)+Xm(q2)), MEAS(q1,q2)]
        seq = [X90(q1), X(q1)*Y(q2), CNOT(q1,q2), Xm(q2), Y(q1)*X(q2)]
        show(seq)
        return seq
    
    def test_compile(self):
        seq = self.test_Operators()
        LL, wfLib = Compiler.compile_sequences(Compiler.normalize(seq))
        assert(len(LL[self.q1]) == 1)
        assert(len(LL[self.q1][0]) == 5)
        assert(len(wfLib[self.q1]) == 4) # X90, X, Y, TAZ
        assert(len(wfLib[self.q2]) == 4) # Y, X, Xm, TAZ
    
    def test_align(self):
        q1 = self.q1
        q2 = self.q2
        seq = [align(X90(q1)*Xtheta(q2, amp=0.5, length=100e-9), 'right'), Y90(q1)*Y90(q2)]
        show(seq)

    def test_composite(self):
        q1 = self.q1
        q2 = self.q2
        flipFlop = X(q1) + X(q1)
        seq = [align(flipFlop * Y(q2)), Y90(q1)]
        show(seq)


if __name__ == "__main__":
    
    unittest.main()
#    singleTest = unittest.TestSuite()
#    singleTest.addTest(SingleQubit("Ramsey"))
#    unittest.TextTestRunner(verbosity=2).run(singleTest)
