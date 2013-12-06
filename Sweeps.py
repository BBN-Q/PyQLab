"""
Various sweeps for scanning experiment parameters
"""

from atom.api import Atom, Str, Float, Int, Bool, Dict, List, Enum, \
    Coerced, Property, observe, cached_property
import enaml
from enaml.qt.qt_application import QtApplication

from instruments.MicrowaveSources import MicrowaveSource
from instruments.Instrument import Instrument

import numpy as np
import json 

class Sweep(Atom):
    name = Str()
    label = Str()
    enabled = Bool(True)
    order = Int(-1)

    def step(self, index):
        pass

class PointsSweep(Sweep):
    """
    A class for sweeps with floating points with one instrument.

    'step' and 'numPoints' both depend on the internal numPoints_ variable to break the dependency cycle
    """
    start = Float()
    step = Property()
    stop = Float()
    numPoints = Property()
    numPoints_ = Int()

    def _set_step(self, step):
        self.numPoints_ = np.arange(self.start, self.stop-2*np.finfo(float).eps, step).size+1

    def _get_step(self):
        return (self.stop - self.start)/max(1, self.numPoints_-1)

    def _set_numPoints(self, numPoints):
        self.numPoints_ = numPoints

    def _get_numPoints(self):
        return self.numPoints_

    @observe('start, stop')
    def update_step(self):
        # update the step to keep numPoints fixed
        newStep = self.step
        self.numPoints_ = -1
        self.step = newStep

class Power(PointsSweep):
    label = 'Power'
    instr = Str()
    units = Enum('dBm', 'Watts').tag(desc='Logarithmic or linear power sweep')

class Frequency(PointsSweep):
    label = 'Frequency'
    instr = Str()

class HeterodyneFrequency(PointsSweep):
    label = 'HeterodyneFrequency'
    instr1 = Str()
    instr2 = Str()
    diffFreq = Float(10.0e-3).tag(desc="IF frequency (GHz)")

class SegmentNum(PointsSweep):
    label = 'SegmentNum'

class SegmentNumWithCals(PointsSweep):
    label = 'SegmentNum'
    stopProxy = Property()
    numCals = Int(0)

    def _set_stopProxy(self, stop):
        self.stop = stop + self.step*self.numCals

    def _get_stopProxy(self):
        return self.stop - self.step*self.numCals

    def _set_step(self, step):
        self.numPoints = np.arange(self.start, self.stop-2*np.finfo(float).eps, step).size+1

    def _get_step(self):
        return (self.stop - self.start)/max(1, self.numPoints-1)

    def _set_numPoints(self, numPoints):
        self.numPoints_ = numPoints + self.numCals

    def _get_numPoints(self):
        return self.numPoints_ - self.numCals
    
class Repeat(Sweep):
    label = 'Repeat'
    numRepeats = Int(1).tag(desc='How many times to loop.')

class AWGChannel(PointsSweep):
    label = 'AWGChannel'
    channel = Enum('1','2','3','4','1&2','3&4').tag(desc='Which channel or pair to sweep')
    mode = Enum('Amp.', 'Offset').tag(desc='Sweeping amplitude or offset')
    instr = Str()

class AWGSequence(Sweep):
    start = Int()
    stop = Int()
    step = Int(1)
    label = 'AWGSequence'
    sequenceFile = Str().tag(desc='Base string for the sequence files')

class Attenuation(PointsSweep):
    label = 'Attenuation (dB)'
    channel = Enum(1, 2, 3).tag(desc='Which channel to sweep')
    instr = Str()

class DC(PointsSweep):
    label = 'DC'
    instr = Str()

class SweepLibrary(Atom):
    sweepDict = Coerced(dict)
    sweepList = Property()
    sweepOrder = List()
    newSweepClasses = List([Power, Frequency, HeterodyneFrequency, Attenuation, SegmentNum, SegmentNumWithCals, AWGChannel, AWGSequence, DC, Repeat]).tag(transient=True)
    possibleInstrs = List()
    libFile = Str().tag(transient=True)

    def __init__(self, **kwargs):
        super(SweepLibrary, self).__init__(**kwargs)
        self.load_from_library()

    #Overload [] to allow direct pulling of sweep info
    def __getitem__(self, sweepName):
        return self.sweepDict[sweepName]

    def _get_sweepList(self):
        return [sweep.name for sweep in self.sweepDict.values() if sweep.enabled]

    # @on_trait_change('[sweepDict.anytrait, sweepOrder]')
    # def write_to_library(self):
    #     import JSONHelpers
    #     if self.libFile:
    #         with open(self.libFile, 'w') as FID:
    #             json.dump(self, FID, cls=JSONHelpers.LibraryEncoder, indent=2, sort_keys=True)

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
    testSource1 = AgilentN5183A(label='TestSource1')
    testSource2 = AgilentN5183A(label='TestSource2')

    from Sweeps import Frequency, Power, SegmentNumWithCals, SweepLibrary
    sweepLib = SweepLibrary(possibleInstrs=[testSource1.label, testSource2.label])
    sweepLib.sweepDict.update({'TestSweep1':Frequency(name='TestSweep1', start=5, step=0.1, stop=6, instr=testSource1.label)})
    sweepLib.sweepDict.update({'TestSweep2':Power(name='TestSweep2', start=-20, stop=0, numPoints=41, instr=testSource2.label)})
    sweepLib.sweepDict.update({'SegWithCals':SegmentNumWithCals(name='SegWithCals', start=0, stopProxy=20, numPoints=101, numCals=4)})
    # sweepLib = SweepLibrary(libFile='Sweeps.json')
    # sweepLib.load_from_library()

    with enaml.imports():
        from SweepsViews import SweepManagerWindow
    app = QtApplication()
    view = SweepManagerWindow(sweepLib=sweepLib)
    view.show()

    app.start()
