# import PulseSequencer
# import Channels
import PatternGen
from PulseSequencer import Pulse

def overrideDefaults(qubit, updateParams):
    '''Helper function to update any parameters passed in and fill in the defaults otherwise.'''
    paramsList = ['pulseType','pulseLength','bufferTime','piAmp','pi2Amp','dragScaling','cutoff']
    #First get the default or updated values
    updateValues = [updateParams[paramName] if paramName in updateParams else getattr(qubit, paramName) for paramName in paramsList]
    #Return a dictionary        
    return {paramName:paramValue for paramName,paramValue in zip(paramsList, updateValues)}

# TODO: update for global caching (no longer chached in channels)
def cachedPulse(pulseFunc):
    ''' Decorator for caching pulses to keep waveform memory usage down. '''
    def cacheWrap(self):
        if pulseFunc.__name__ not in self.pulseCache:
            self.pulseCache[pulseFunc.__name__] = pulseFunc(self)
        return self.pulseCache[pulseFunc.__name__]
    
    return cacheWrap

def Id(qubit, width=0, **kwargs):
    ''' A delay or do-nothing in the form of a pulse i.e. it will take pulseLength+2*bufferTime. '''
    shape = PatternGen.Delay(amp=0, phase=0, pulseLength=width)
    return Pulse("Id", (qubit), shape, 0.0)

def Xtheta(qubit, amp=0, **kwargs):
    '''  A generic X rotation with a variable amplitude  '''
    shape = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else qubit.pulseType](amp=amp, phase=0, **overrideDefaults(qubit, kwargs))
    return Pulse("Xtheta", (qubit), shape, 0.0)

def Ytheta(qubit, amp=0, **kwargs):
    ''' A generic Y rotation with a variable amplitude '''
    shape = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else qubit.pulseType](amp=amp, phase=0.25, **overrideDefaults(qubit, kwargs))
    return Pulse("Ytheta", (qubit), shape, 0.0)
    
def U90(qubit, phase=0, **kwargs):
    ''' A generic 90 degree rotation with variable phase. Phase is defined in portions of a circle. '''
    shape = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else qubit.pulseType](amp=qubit.pi2Amp, phase=phase, **overrideDefaults(qubit, kwargs))
    return Pulse("U90", (qubit), shape, 0.0)

def U180(qubit, phase=0, **kwargs):
    ''' A generic 180 degree rotation with variable phase.  '''
    shape = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else qubit.pulseType](amp=qubit.piAmp, phase=phase, **overrideDefaults(qubit, kwargs))
    return Pulse("U180", (qubit), shape, 0.0)
    
def Utheta(qubit, amp=0, phase=0, **kwargs):
    '''  A generic rotation with variable amplitude and phase. '''
    shape = PatternGen.pulseDict[kwargs['pulseType'] if 'pulseType' in kwargs else qubit.pulseType](amp=amp, phase=phase, **overrideDefaults(qubit, kwargs))
    return Pulse("Utheta", (qubit), shape, 0.0)

#Setup the default 90/180 rotations
# @cachedPulse
def X(qubit):
    shape = PatternGen.pulseDict[qubit.pulseType](amp=qubit.piAmp, phase=0, **overrideDefaults(qubit, {}))
    return Pulse("X", (qubit), shape, 0.0)
    
# @cachedPulse
def X90(qubit):
    shape = PatternGen.pulseDict[qubit.pulseType](amp=qubit.pi2Amp, phase=0, **overrideDefaults(qubit, {}))
    return Pulse("X90", (qubit), shape, 0.0)

# @cachedPulse
def Xm(qubit):
    shape = PatternGen.pulseDict[qubit.pulseType](amp=qubit.piAmp, phase=0.5, **overrideDefaults(qubit, {}))
    return Pulse("Xm", (qubit), shape, 0.0)
    
# @cachedPulse
def X90m(qubit):
    shape = PatternGen.pulseDict[qubit.pulseType](amp=qubit.pi2Amp, phase=0.5, **overrideDefaults(qubit, {}))
    return Pulse("X90m", (qubit), shape, 0.0)

# @cachedPulse
def Y(qubit):
    shape = PatternGen.pulseDict[qubit.pulseType](amp=qubit.piAmp, phase=0.25, **overrideDefaults(qubit, {}))
    return Pulse("Y", (qubit), shape, 0.0)

# @cachedPulse
def Y90(qubit):
    shape = PatternGen.pulseDict[qubit.pulseType](amp=qubit.pi2Amp, phase=0.25, **overrideDefaults(qubit, {}))
    return Pulse("Y90", (qubit), shape, 0.0)

# @cachedPulse
def Ym(qubit):
    shape = PatternGen.pulseDict[qubit.pulseType](amp=qubit.piAmp, phase=0.75, **overrideDefaults(qubit, {}))
    return Pulse("Ym", (qubit), shape, 0.0)

# @cachedPulse
def Y90m(qubit):
    shape = PatternGen.pulseDict[qubit.pulseType](amp=qubit.pi2Amp, phase=0.75, **overrideDefaults(qubit, {}))
    return Pulse("Y90m", (qubit), shape, 0.0)

## two-qubit primitivies
def CNOT(source, target):
    # TODO construct the (source, target) channel and pull parameters from there
    # something like: channel = Qubit((source, target))
    shape = PatternGen.pulseDict[source.pulseType](amp=source.piAmp, phase=0.0, **overrideDefaults(source, {}))
    return Pulse("CNOT", (source, target), shape, 0.0)