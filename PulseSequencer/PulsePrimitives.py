import PulseSequencer
import Channels

def overrideDefaults(self, updateParams):
    '''Helper function to update any parameters passed in and fill in the defaults otherwise.'''
    paramsList = ['pulseType','pulseLength','bufferTime','piAmp','pi2Amp','dragScaling', 'cutoff']
    #First get the default or updated values
    updateValues = [updateParams[tmpName] if tmpName in updateParams else getattr(self, tmpName) for tmpName in paramsList]
    #Return a dictionary        
    return {paramName:paramValue for paramName,paramValue in zip(paramsList, updateValues)}

def Id(qubit, **kwargs):
    ''' A delay or do-nothing in the form of a pulse i.e. it will take pulseLength+2*bufferTime. '''
    shape = PatternGen.QId(**overrideDefaults(kwargs)), qubit)    
    return Pulse("Id", [qubit], shape, 0.0)

def Xtheta(qubit, amp=0, **kwargs):
    '''  A generic X rotation with a variable amplitude  '''
    tmpPulse = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else self.pulseType](amp=amp, phase=0, **self.overrideDefaults(kwargs))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock

def Ytheta(qubit, amp=0, **kwargs):
    ''' A generic Y rotation with a variable amplitude '''
    tmpPulse = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else self.pulseType](amp=amp, phase=0.25, **self.overrideDefaults(kwargs))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock
    
def U90(qubit, phase=0, **kwargs):
    ''' A generic 90 degree rotation with variable phase. Phase is defined in portions of a circle. '''
    tmpPulse = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else self.pulseType](amp=self.pi2Amp, phase=phase, **self.overrideDefaults(kwargs))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock

def U180(qubit, phase=0, **kwargs):
    ''' A generic 180 degree rotation with variable phase.  '''
    tmpPulse = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else self.pulseType](amp=self.piAmp, phase=phase, **self.overrideDefaults(kwargs))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock
    
def Utheta(qubit, amp=0, phase=0, **kwargs):
    '''  A generic rotation with variable amplitude and phase. '''
    tmpPulse = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else self.pulseType](amp=amp, phase=phase, **self.overrideDefaults(kwargs))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock

#Setup the default 90/180 rotations
@cachedPulse
def Xp(self):
    tmpPulse = PatternGen.pulseDict[self.pulseType](amp=self.piAmp, phase=0, **self.overrideDefaults({}))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock
    
@cachedPulse
def X90p(self):
    tmpPulse = PatternGen.pulseDict[self.pulseType](amp=self.pi2Amp, phase=0, **self.overrideDefaults({}))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock

@cachedPulse
def Xm(self):
    tmpPulse = PatternGen.pulseDict[self.pulseType](amp=self.piAmp, phase=0.5, **self.overrideDefaults({}))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock
    
@cachedPulse
def X90m(self):
    tmpPulse = PatternGen.pulseDict[self.pulseType](amp=self.pi2Amp, phase=0.5, **self.overrideDefaults({}))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock
    
@cachedPulse
def Yp(self):
    tmpPulse = PatternGen.pulseDict[self.pulseType](amp=self.piAmp, phase=0.25, **self.overrideDefaults({}))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock
    
@cachedPulse
def Y90p(self):
    tmpPulse = PatternGen.pulseDict[self.pulseType](amp=self.pi2Amp, phase=0.25, **self.overrideDefaults({}))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock
   
@cachedPulse
def Ym(self):
    tmpPulse = PatternGen.pulseDict[self.pulseType](amp=self.piAmp, phase=0.75, **self.overrideDefaults({}))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock
    
@cachedPulse
def Y90m(self):
    tmpPulse = PatternGen.pulseDict[self.pulseType](amp=self.pi2Amp, phase=0.75, **self.overrideDefaults({}))
    tmpBlock = PulseSequencer.PulseBlock()
    tmpBlock.add_pulse(tmpPulse, self)
    return tmpBlock