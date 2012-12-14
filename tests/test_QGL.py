import unittest
import numpy as np


from QGL import *


class SingleQubit(unittest.TestCase):
    def setUp(self):
        self.q1 = Qubit('q1', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)

    def test_Ramsey(self):
        '''
        Test simple Ramsey sequence
        '''
        q1 = self.q1
        ramsey = [[X90(q1), Id(q1, delay), X90(q1)] for delay in np.linspace(0.0, 1e-6, 11)]
        show(ramsey[2])
        return ramsey
    
    def test_compile(self):
        seq = self.test_Ramsey()
        LL, wfLib = Compiler.compile_sequences(seq)
        assert(len(LL[self.q1]) == 11)
        assert(len(LL[self.q1][0]) == 2)
        print [len(miniLL) == 3 for miniLL in LL[self.q1][1:]]
        assert( all([len(miniLL) == 3 for miniLL in LL[self.q1][1:]]) )
        assert(len(wfLib[self.q1]) == 12) # 10 non-zero delays + X90 + TAZ

class MultiQubit(unittest.TestCase):

    def test_Operators(self):
        q1 = Qubit('q1', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
        # goal is to make this just: q1 = Qubit('q1')
        q2 = Qubit('q2', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
        # seq = [X90(q1), X(q1)*Y(q2), CNOT(q1,q2), X(q2)+Xm(q2), Y(q1)*(X(q2)+Xm(q2)), MEAS(q1,q2)]
        seq = [X90(q1), X(q1)*Y(q2), CNOT(q1,q2), Xm(q2), Y(q1)*X(q2)]
        show(seq)
        return seq
    
    def test_compile(self):
        seq = self.test_Operators()
        LL, wfLib = Compiler.compile_sequence(seq)
    
    def test_align(self):
        q1 = Qubit('q1', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
        # goal is to make this just: q1 = Qubit('q1')
        q2 = Qubit('q2', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
        seq = [align(X90(q1)*Utheta(q1, 'pulseLength=100e-9'), 'right'), Y90(q1)*Y90(q2)]
        show(seq)


if __name__ == "__main__":
    
    unittest.main()
#    singleTest = unittest.TestSuite()
#    singleTest.addTest(SingleQubit("Ramsey"))
#    unittest.TextTestRunner(verbosity=2).run(singleTest)
