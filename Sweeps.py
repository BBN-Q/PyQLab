"""
Various sweeps for scanning experiment parameters
"""

from traits.api import HasTraits, Str, Float, Int, Bool, Dict, List, Enum, \
    Instance, Property, Array, cached_property, TraitListObject, on_trait_change
import enaml

from instruments.MicrowaveSources import MicrowaveSource
from instruments.Instrument import Instrument

import abc
import numpy as np
import json 

class Sweep(HasTraits):
    name = Str
    label = Str
    enabled = Bool(True)
    order = Int(-1)

    @abc.abstractmethod
    def step(self, index):
        pass

class PointsSweep(Sweep):
    """
    A class for sweeps with floating points with one instrument.

    'step' and 'numPoints' both depend on the internal numPoints_ variable to break the dependency cycle
    """
    start = Float
    step = Property(depends_on=['numPoints_'])
    stop = Float
    numPoints = Property(depends_on=['step'])
    numPoints_ = Int

    def _set_step(self, step):
        self.numPoints_ = np.arange(self.start, self.stop-2*np.finfo(float).eps, step).size+1

    def _get_step(self):
        return (self.stop - self.start)/max(1, self.numPoints_-1)

    def _set_numPoints(self, numPoints):
        self.numPoints_ = numPoints

    def _get_numPoints(self):
        return self.numPoints_

    @on_trait_change('[start, stop]')
    def update_step(self):
        # update the step to keep numPoints fixed
        newStep = self.step
        self.numPoints_ = -1
        self.step = newStep

class Power(PointsSweep):
    label = 'Power'
    instr = Str
    units = Enum('dBm', 'Watts', desc='Logarithmic or linear power sweep')

class Frequency(PointsSweep):
    label = 'Frequency'
    instr = Str

class SegmentNum(PointsSweep):
    label = 'SegmentNum'
    
class Repeat(Sweep):
    label = 'Repeat'
    numRepeats = Int(1, desc='How many times to loop.')

class AWGChannel(PointsSweep):
    label = 'AWGChannel'
    channel = Enum('1','2','3','4','1&2','3&4', desc='Which channel or pair to sweep')
    mode = Enum('Amp.', 'Offset', desc='Sweeping amplitude or offset')
    instr = Str

class AWGSequence(Sweep):
    start = Int
    stop = Int
    step = Int(1)
    label = 'AWGSequence'
    sequenceFile = Str('', desc='Base string for the sequence files')

class Attenuation(PointsSweep):
    label = 'Attenuation (dB)'
    channel = Enum(1, 2, 3, desc='Which channel to sweep')
    instr = Str

class DC(PointsSweep):
    label = 'DC'
    instr = Str

class SweepLibrary(HasTraits):
    sweepDict = Dict(Str, Sweep)
    sweepList = Property(List, depends_on='sweepDict.anytrait')
    sweepOrder = List(Str)
    newSweepClasses = List([Power, Frequency, Attenuation, SegmentNum, AWGChannel, AWGSequence, DC, Repeat], transient=True)
    possibleInstrs = List(Str)
    libFile = Str(transient=True)

    def __init__(self, **kwargs):
        super(SweepLibrary, self).__init__(**kwargs)
        self.load_from_library()

    #Overload [] to allow direct pulling of sweep info
    def __getitem__(self, sweepName):
        return self.sweepDict[sweepName]

    @cached_property
    def _get_sweepList(self):
        return [sweep.name for sweep in self.sweepDict.values() if sweep.enabled]

    @on_trait_change('[sweepDict.anytrait, sweepOrder]')
    def write_to_library(self):
        import JSONHelpers
        if self.libFile:
            with open(self.libFile, 'w') as FID:
                json.dump(self, FID, cls=JSONHelpers.LibraryEncoder, indent=2, sort_keys=True)

    def load_from_library(self):
        import JSONHelpers
        if self.libFile:
            try:
                with open(self.libFile, 'r') as FID:
                    tmpLib = json.load(FID, cls=JSONHelpers.LibraryDecoder)
                    if isinstance(tmpLib, SweepLibrary):
                        self.sweepDict.update(tmpLib.sweepDict)
                        del self.possibleInstrs[:]
                        for instr in tmpLib.possibleInstrs:
                            self.possibleInstrs.append(instr)
                        del self.sweepOrder[:]
                        for sweepStr in tmpLib.sweepOrder:
                            self.sweepOrder.append(sweepStr)
            except IOError:
                print('No sweep library found.')

if __name__ == "__main__":
    from instruments.MicrowaveSources import AgilentN5183A  
    testSource1 = AgilentN5183A(name='TestSource1')
    testSource2 = AgilentN5183A(name='TestSource2')

    from Sweeps import Frequency, Power, SweepLibrary
    # sweepLib = SweepLibrary(possibleInstrs=[testSource1.name, testSource2.name])
    # sweepLib.sweepDict.update({'TestSweep1':Frequency(name='TestSweep1', start=5, stop=6, step=0.1, instr=testSource1.name)
    # sweepLib.sweepDict.update({'TestSweep2':Power(name='TestSweep2', start=-20, stop=0, step=0.5, instr=testSource2.name)
    sweepLib = SweepLibrary(libFile='SweepLibrary.json')
    sweepLib.load_from_library()

    from enaml.stdlib.sessions import show_simple_view

    with enaml.imports():
        from SweepsViews import SweepManagerWindow
    session = show_simple_view(SweepManagerWindow(sweepLib=sweepLib))
