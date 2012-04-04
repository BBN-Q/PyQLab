'''
Created on Jan 8, 2012

Somewhat mimic Blake's PatternGen for creating pulse shapes.
@author: cryan
'''
import numpy as np



class Pulse(object):
    '''
    The basic pulse shape which will be inherited.
    '''
    def __init__(self, time=None, bufferTime=None, amp=None, phase=None):
        self.time = time
        self.bufferTime = 0 if bufferTime is None else bufferTime
        self.amp = 0 if amp is None else amp
        self.phase = 0 if phase is None else phase
        
    #Generate the bare shape: should be overwritten in subclasses
    def generateShape(self):
        return np.array([])

    #Create the full patter with buffering points    
    def generatePattern(self, AWGFreq):
        bufferPts = round(self.bufferTime*AWGFreq)
        return np.hstack((np.zeros(bufferPts), np.exp(-1j*2*np.pi*self.phase)*self.amp*self.generateShape(AWGFreq), np.zeros(bufferPts)))

    def numPoints(self, AWGFreq):
        return 2*round(self.bufferTime*AWGFreq) + round(self.time*AWGFreq)
    
    
'''
Some basic shapes.
'''
class Gaussian(Pulse):
    '''
    A simple gaussian shaped pulse. 
    cutoff is how many sigma the pulse goes out
    '''
    def __init__(self, time=None, cutoff=2, bufferTime=None, amp=None, phase=None):
        super(Gaussian, self).__init__(time, bufferTime, amp, phase)
        self.cutoff = cutoff
        
    def generateShape(self, AWGFreq):
        #Round to how many points we need
        numPts = np.round(self.time*AWGFreq)
        xPts = np.linspace(-self.cutoff, self.cutoff, numPts)
        return np.exp(-0.5*xPts**2)
        
class Square(Pulse):
    '''
    A simple rectangular shaped pulse. 
    cutoff is how many sigma the pulse goes out
    '''
    def __init__(self, time=None):
        super(Square, self).__init__(time)
                
    def generateShape(self, AWGFreq):
        #Round to how many points we need
        numPts = round(self.time*AWGFreq)
        return np.ones(numPts)

'''
Dictionary linking pulse names to functions.
'''
pulseDict = {'square':Square,'gauss':Gaussian}



if __name__ == '__main__':
    pass