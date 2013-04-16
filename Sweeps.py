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
    numSteps = Int
    enabled = Bool(True)

    @abc.abstractmethod
    def step(self, index):
        pass

class PointsSweep(Sweep):
    """
    A class for sweeps with floating points with one instrument
    """
    start = Float
    step = Float
    stop = Property(depends_on=['start', 'step', 'numPoints'])
    numPoints = Int
    points = Property(depends_on=['start', 'step', 'numPoints'])

    #if either the number of points or the stop is updated then update the other
    def _set_stop(self, stop):
        self.numPoints = np.arange(self.start, stop-2*np.finfo(float).eps, self.step).size+1 if self.step else 0

    def _get_stop(self):
        return self.start + (self.numPoints-1)*self.step

    @cached_property
    def _get_points(self):
        if self.step:
            return np.arange(self.start, self.start+self.numPoints*self.step, self.step)
        else:
            return None

class Power(PointsSweep):
    label = 'Power'
    instr = Str

class Frequency(PointsSweep):
    label = 'Frequency'
    instr = Str

class SegmentNum(PointsSweep):
    label = 'SegmentNum'
    pass

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

class SweepLibrary(HasTraits):
    sweepDict = Dict(Str, Sweep)
    sweepList = Property(List, depends_on='sweepDict')
    sweepOrder = List(Str)
    newSweepClasses = List([Power, Frequency, SegmentNum, AWGChannel, AWGSequence], transient=True)
    possibleInstrs = List(Str)
    libFile = Str(transient=True)

    def __init__(self, **kwargs):
        super(SweepLibrary, self).__init__(**kwargs)
        self.load_from_library()

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
