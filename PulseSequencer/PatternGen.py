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
    def __init__(self, time=None, bufferTime=None):
        self.time = time
        self.bufferTime = 0 if bufferTime is None else bufferTime
     
    #Generate the bare shape: should be overwritten in subclasses
    def generateShape(self):
        return np.array([])

    #Create the full patter with buffering points    
    def generatePattern(self, AWGFreq):
        bufferPts = round(self.bufferTime*AWGFreq)
        return np.hstack((np.zeros(bufferPts), self.generateShape(AWGFreq), np.zeros(bufferPts)))

    def numPoints(self, AWGFreq):
        return round(self.bufferTime*AWGFreq) + round(self.time*AWGFreq)
'''
Some basic shapes.
'''
class Gaussian(Pulse):
    '''
    A simple gaussian shaped pulse. 
    cutoff is how many sigma the pulse goes out
    '''
    def __init__(self, cutoff=2, time=None):
        super(Gaussian, self).__init__(time)
        self.cutoff = cutoff
        
    def generateShape(self, AWGFreq):
        #Round to how many points we need
        numPts = np.round(self.time*AWGFreq)
        xPts = np.linspace(-self.cutoff, self.cutoff, numPts)
        return np.exp(0.5*xPts)
        
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

if __name__ == '__main__':
    pass