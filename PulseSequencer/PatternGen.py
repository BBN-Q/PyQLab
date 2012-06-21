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
    def __init__(self, pulseLength=None, bufferTime=None, amp=None, phase=None, isTimeAmp=None, **kwargs):
        self.pulseLength = pulseLength
        self.bufferTime = 0 if bufferTime is None else bufferTime
        self.amp = 0 if amp is None else amp
        self.phase = 0 if phase is None else phase
        self.isTimeAmp = False if isTimeAmp is None else isTimeAmp
        
    #Generate the bare shape: should be overwritten in subclasses
    def generateShape(self):
        return np.array([])

    #Create the full patter with buffering points    
    def generatePattern(self, AWGFreq):
        bufferPts = round(self.bufferTime*AWGFreq)
        return np.hstack((np.zeros(bufferPts), np.exp(1j*2*np.pi*self.phase)*self.amp*self.generateShape(AWGFreq), np.zeros(bufferPts)))

    def numPoints(self, AWGFreq):
        return int(2*round(self.bufferTime*AWGFreq) + round(self.pulseLength*AWGFreq))
    
    
'''
Some basic shapes.
'''
class Gaussian(Pulse):
    '''
    A simple gaussian shaped pulse. 
    cutoff is how many sigma the pulse goes out
    '''
    def __init__(self, pulseLength=None, cutoff=2, **kwargs):
        super(Gaussian, self).__init__(pulseLength, **kwargs)
        self.cutoff = cutoff
        
    def generateShape(self, AWGFreq):
        #Round to how many points we need
        numPts = np.round(self.pulseLength*AWGFreq)
        xPts = np.linspace(-self.cutoff, self.cutoff, numPts)
        xStep = xPts[1] - xPts[0]
        return np.exp(-0.5*(xPts**2)) - np.exp(-0.5*((xPts[-1]+xStep)**2))
        
class Square(Pulse):
    '''
    A simple rectangular shaped pulse. 
    '''
    def __init__(self, pulseLength=None, **kwargs):
        super(Square, self).__init__(pulseLength, **kwargs)
                
    def generateShape(self, AWGFreq):
        #Round to how many points we need
        numPts = round(self.pulseLength*AWGFreq)
        return np.ones(numPts)
        
class QId(Pulse):
    '''
    A delay between pulses.
    '''
    def __init__(self, pulseLength=None, **kwargs):
        super(QId, self).__init__(pulseLength=pulseLength, isTimeAmp=True, **kwargs)
        
    def generateShape(self, AWGFreq):
        #Return a single point at 0
        return np.zeros(1, dtype=np.complex)

    def generatePattern(self, AWGFreq):
        #Overload to also return only a single point
        return np.zeros(1, dtype=np.complex)

class DRAG(Pulse):
    '''
    A gaussian pulse with a drag correction on the quadrature channel.
    '''
    def __init__(self, pulseLength=None, dragScaling=0, cutoff=2, **kwargs):
        super(DRAG, self).__init__(pulseLength, **kwargs)
        self.cutoff=2
        self.dragScaling = dragScaling
        
    def generateShape(self, AWGFreq):
        #Create the gaussian along x and the derivative along y
        numPts = np.round(self.pulseLength*AWGFreq)
        xPts = np.linspace(-self.cutoff, self.cutoff, numPts)
        xStep = xPts[1] - xPts[0]
        IQuad = np.exp(-0.5*(xPts**2)) - np.exp(-0.5*((xPts[0]-xStep)**2))
        #The derivative needs to be scaled in terms of AWG points from the normalized xPts units.
        #The pulse length is 2*cutoff xPts
        derivScale = 1/(self.pulseLength/2/self.cutoff*AWGFreq)
        QQuad = self.dragScaling*derivScale*xPts*IQuad
        return IQuad+1j*QQuad
        

        
'''
Dictionary linking pulse names to functions.
'''
pulseDict = {'square':Square,'gauss':Gaussian,'drag':DRAG}



if __name__ == '__main__':
    pass