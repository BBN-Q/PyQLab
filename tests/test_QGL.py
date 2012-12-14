import unittest
import numpy as np


from QGL import *


class SingleQubit(unittest.TestCase):

    def test_Ramsey(self):
        '''
        Test simple Ramsey sequence
        '''
        q1 = Qubit('q1', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
        ramsey = [[X90(q1), Id(q1, delay), X90(q1)] for delay in np.linspace(0.0, 1e-6, 11)]
        show(ramsey[2])
        

class MultiQubit(unittest.TestCase):

    def test_Operators(self):
        q1 = Qubit('q1', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
        # goal is to make this just: q1 = Qubit('q1')
        q2 = Qubit('q2', piAmp=1.0, pi2Amp=0.5, pulseLength=30e-9)
        # seq = [X90(q1), X(q1)*Y(q2), CNOT(q1,q2), X(q2)+Xm(q2), Y(q1)*(X(q2)+Xm(q2)), MEAS(q1,q2)]
        seq = [X90(q1), X(q1)*Y(q2), CNOT(q1,q2), Xm(q2), Y(q1)*X(q2)]
        show(seq)
        #compileSeq(seq)
    
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
