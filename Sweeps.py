"""
Various sweeps for scanning experiment parameters
"""

from atom.api import Atom, Str, Float, Int, Bool, Dict, List, Enum, \
    Coerced, Property, Typed, observe, cached_property, Int
import enaml
from enaml.qt.qt_application import QtApplication

from instruments.MicrowaveSources import MicrowaveSource
from instruments.Instrument import Instrument

from DictManager import DictManager

import numpy as np
import json
import floatbits

class Sweep(Atom):
    label = Str()
    axisLabel = Str()
    enabled = Bool(True)
    order = Int(-1)

    def json_encode(self, matlabCompatible=False):
        jsonDict = self.__getstate__()
        if matlabCompatible:
            jsonDict['type'] = self.__class__.__name__
            jsonDict.pop('enabled', None)
            jsonDict.pop('name', None)
        else:
            jsonDict['x__class__'] = self.__class__.__name__
            jsonDict['x__module__'] = self.__class__.__module__
        return jsonDict

class PointsSweep(Sweep):
    """
    A class for sweeps with floating points with one instrument.

    'step' depends on numPoints (but not the other way around) to break the dependency cycle
    """
    start = Float(1.0)
    step = Property()
    stop = Float(1.0)
    numPoints = Int(1)

    def _set_step(self, step):
        # int() will give floor() casted to an Int
        self.numPoints = int((self.stop - self.start)/floatbits.prevfloat(step)) + 1

    def _get_step(self):
        return (self.stop - self.start)/max(1, self.numPoints-1)

    @observe('start', 'stop', 'numPoints')
    def update_step(self, change):
        if change['type'] == 'update':
            # update the step to keep numPoints fixed
            self.get_member('step').reset(self)

class Power(PointsSweep):
    label = Str(default='Power')
    instr = Str()
    units = Enum('dBm', 'Watts').tag(desc='Logarithmic or linear power sweep')

class Frequency(PointsSweep):
    label = Str(default='Frequency')
    instr = Str()

class HeterodyneFrequency(PointsSweep):
    label = Str(default='HeterodyneFrequency')
    instr1 = Str()
    instr2 = Str()
    diffFreq = Float(10.0e-3).tag(desc="IF frequency (GHz)")

class SegmentNum(PointsSweep):
    label = Str(default='SegmentNum')

class SegmentNumWithCals(PointsSweep):
    label = Str(default='SegmentNumWithCals')
    numCals = Int(0)

    def json_encode(self, matlabCompatible=False):
        jsonDict = super(SegmentNumWithCals, self).json_encode(matlabCompatible)
        if matlabCompatible:
            jsonDict['type'] = 'SegmentNum'
            jsonDict['stop'] = self.stop + self.step * self.numCals
            jsonDict['numPoints'] = self.numPoints + self.numCals
        return jsonDict
    
class Repeat(Sweep):
    label = Str(default='Repeat')
    numRepeats = Int(1).tag(desc='How many times to loop.')

class AWGChannel(PointsSweep):
    label = Str(default='AWGChannel')
    channel = Enum('1','2','3','4','1&2','3&4').tag(desc='Which channel or pair to sweep')
    mode = Enum('Amp.', 'Offset').tag(desc='Sweeping amplitude or offset')
    instr = Str()

class AWGSequence(Sweep):
    label = Str(default='AWGSequence')
    start = Int()
    stop = Int()
    step = Int(1)
    sequenceFile = Str().tag(desc='Base string for the sequence files')

class Attenuation(PointsSweep):
    label = Str(default='Attenuation (dB)')
    channel = Enum(1, 2, 3).tag(desc='Which channel to sweep')
    instr = Str()

class DC(PointsSweep):
    label = Str(default='DC')
    instr = Str()

class Threshold(PointsSweep):
    label = Str(default="Threshold")
    instr = Str()
    stream = Enum('(1,1)','(1,2)','(2,1)','(2,2)').tag(desc='which stream to set threshold')

newSweepClasses = [Power, Frequency, HeterodyneFrequency, Attenuation, SegmentNum, SegmentNumWithCals, AWGChannel, AWGSequence, DC, Repeat, Threshold]

class SweepLibrary(Atom):
    sweepDict = Coerced(dict)
    sweepList = Property()
    sweepOrder = List()
    possibleInstrs = List()
    version = Int(1)

    sweepManager = Typed(DictManager)

    libFile = Str()

    def __init__(self, **kwargs):
        super(SweepLibrary, self).__init__(**kwargs)
        self.load_from_library()
        self.sweepManager = DictManager(itemDict=self.sweepDict,
                                        possibleItems=newSweepClasses)

    #Overload [] to allow direct pulling of sweep info
    def __getitem__(self, sweepName):
        return self.sweepDict[sweepName]

    def _get_sweepList(self):
        return [sweep.label for sweep in self.sweepDict.values() if sweep.enabled]

    def write_to_file(self):
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

    def json_encode(self, matlabCompatible=False):
            if matlabCompatible:
                #  re-assign based on sweepOrder
                for ct, sweep in enumerate(self.sweepOrder):
                  self.sweepDict[sweep].order = ct+1
                return {label:sweep for label,sweep in self.sweepDict.items() if label in self.sweepOrder}
            else:
                return {'sweepDict':{label:sweep for label,sweep in self.sweepDict.items()}, 'sweepOrder':self.sweepOrder}





if __name__ == "__main__":
    from instruments.MicrowaveSources import AgilentN5183A  
    testSource1 = AgilentN5183A(label='TestSource1')
    testSource2 = AgilentN5183A(label='TestSource2')

    from Sweeps import Frequency, Power, SegmentNumWithCals, SweepLibrary
    sweepDict = {
        'TestSweep1': Frequency(label='TestSweep1', start=5, step=0.1, stop=6, instr=testSource1.label),
        'TestSweep2': Power(label='TestSweep2', start=-20, stop=0, numPoints=41, instr=testSource2.label),
        'SegWithCals': SegmentNumWithCals(label='SegWithCals', start=0, stop=20, numPoints=101, numCals=4)
    }
    sweepLib = SweepLibrary(possibleInstrs=[testSource1.label, testSource2.label], sweepDict=sweepDict)
    # sweepLib = SweepLibrary(libFile='Sweeps.json')

    with enaml.imports():
        from SweepsViews import SweepManagerWindow
    app = QtApplication()
    view = SweepManagerWindow(sweepLib=sweepLib)
    view.show()

    app.start()
