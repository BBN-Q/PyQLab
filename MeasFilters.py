"""
Measurement filters
"""

from atom.api import Atom, Int, Float, List, Str, Dict, Bool, Enum, Coerced, Typed, observe, Instance
import enaml
from enaml.qt.qt_application import QtApplication
from instruments.Digitizers import AlazarATS9870, X6
from DictManager import DictManager
import json
from JSONLibraryUtils import LibraryCoders

class MeasFilter(Atom):
    label = Str()
    enabled = Bool(True)
    dataSource = Str().tag(desc="Where the measurement data is pushed from.")

    def json_encode(self, matlabCompatible=False):
        jsonDict = self.__getstate__()
        if matlabCompatible:
            jsonDict['filterType'] = self.__class__.__name__
            jsonDict.pop('enabled', None)
            jsonDict.pop('label', None)
            import numpy as np
            import base64
            try:
                jsonDict['kernel'] = base64.b64encode(eval(self.kernel))
            except:
                jsonDict['kernel'] = []
        else:
            jsonDict['x__class__'] = self.__class__.__name__
            jsonDict['x__module__'] = self.__class__.__module__
        return jsonDict

class Plotter(MeasFilter):
    label    = Str()
    enabled  = Bool(True)
    plotMode = Enum('amp/phase', 'real/imag', 'quad').tag(desc='Filtered data scope mode.')

class WriteToHDF5(MeasFilter):
    label       = Str()
    enabled     = Bool(True)
    filename    = Str('').tag(desc='Path to file where records will be saved.')
    compression = Bool(True)

class AlazarStreamSelector(MeasFilter):
    digitizer = Instance((str, AlazarATS9870))
    channel   = Str().tag(desc="Which channel to select from the Alazar")

class X6StreamSelector(MeasFilter):
    digitizer               = Instance((str, X6))
    label                   = Str()
    enableDemodStream       = Bool(True).tag(desc='Enable demodulated data stream')
    enableDemodResultStream = Bool(True).tag(desc='Enable demod result data stream')
    enableRawResultStream   = Bool(True).tag(desc='Enable raw result data stream')
    IFfreq                  = Float(10e6).tag(desc='IF Frequency')
    demodKernel             = Str().tag(desc='Integration kernel vector for demod stream')
    demodKernelBias         = Str("").tag(desc="Kernel bias for integrated demod stream")
    rawKernel               = Str().tag(desc='Integration kernel vector for raw stream')
    rawKernelBias           = Str("").tag(desc="Kernel bias for integrated raw stream")
    threshold               = Float(0.0).tag(desc='Qubit state decision threshold')
    thresholdInvert         = Bool(False).tag(desc="Invert thresholder output")

    def json_encode(self, matlabCompatible=False):
        jsonDict = self.__getstate__()
        if matlabCompatible:
            import numpy as np
            import base64
            try:
                jsonDict['demodKernel'] = base64.b64encode(eval(self.demodKernel))
            except:
                jsonDict['demodKernel'] = []
            try:
                jsonDict['demodKernelBias'] = base64.b64encode(np.array(eval(self.demodKernelBias), dtype=np.complex128))
            except:
                jsonDict['demodKernelBias'] = []
            try:
                jsonDict['rawKernel'] = base64.b64encode(eval(self.rawKernel))
            except:
                jsonDict['rawKernel'] = []
            try:
                jsonDict['rawKernelBias'] = base64.b64encode(np.array(eval(self.rawKernelBias), dtype=np.complex128))
            except:
                jsonDict['rawKernelBias'] = []
        return jsonDict

class DigitalDemod(MeasFilter):
    IFfreq = Float(10e6).tag(desc='The I.F. frequency for digital demodulation.')
    bandwidth = Float(5e6).tag(desc='Low-pass filter bandwidth')
    samplingRate = Float(250e6).tag(desc='The sampling rate of the digitizer.')
    phase = Float(0.0).tag(desc='Phase rotation to apply in rad.')
    decimFactor1 = Int(1).tag(desc="First stage polyphase decimation (before multiplication with reference).")
    decimFactor2 = Int(1).tag(desc="Second stage polyphase decimation (before IIR filter).")
    decimFactor3 = Int(1).tag(desc="Third stage polyphase decimation (after IIR filter).")

class KernelIntegration(MeasFilter):
    kernel = Str('').tag(desc="Integration kernel vector.")
    bias = Float(0.0).tag(desc="Bias after integration.")
    simpleKernel = Bool(True)
    boxCarStart = Int(1)
    boxCarStop = Int(1)
    IFfreq = Float(10e6)
    samplingRate = Float(250e6)

    def json_encode(self, matlabCompatible=False):
        jsonDict = super(KernelIntegration, self).json_encode(matlabCompatible)
        if matlabCompatible:
            # re-encode kernel in base64
            jsonDict.pop('kernel')

            import numpy as np
            import base64
            try:
                if self.simpleKernel:
                    kernel = np.hstack((np.zeros(self.boxCarStart, dtype=np.complex), np.ones(self.boxCarStop-self.boxCarStart)))
                    kernel *= np.exp(1j*2*np.pi*self.IFfreq*np.arange(self.boxCarStop)/self.samplingRate)
                    kernel = base64.b64encode(kernel)
                else:
                    kernel = base64.b64encode(eval(self.kernel))
            except:
                kernel = []
            jsonDict['kernel'] = kernel
        return jsonDict

class Correlator(MeasFilter):
    filters = List()

    def __init__(self, **kwargs):
        super(Correlator, self).__init__(**kwargs)
        if not self.filters:
            self.filters = [None, None]

    def json_encode(self, matlabCompatible=False):
        jsonDict = super(Correlator, self).json_encode(matlabCompatible)
        #For correlation filters return the filter list as a list of filter names
        filterList = jsonDict.pop('filters')
        jsonDict['filters'] = [item.label for item in filterList] if filterList else []
        jsonDict['dataSource'] = ','.join(jsonDict['filters']) # correlator has mulitple data sources which are one and the same as the filter list
        return jsonDict

class StateComparator(MeasFilter):
    threshold = Float(0.0)
    integrationTime = Int(-1).tag(desc='Comparator integration time in decimated samples, use -1 for the entire record')

class MeasFilterLibrary(Atom):
    # filterDict = Dict(Str, MeasFilter)
    filterDict = Coerced(dict)
    libFile = Str().tag(transient=True)
    filterManager = Typed(DictManager)
    version = Int(1)

    def __init__(self, **kwargs):
        super(MeasFilterLibrary, self).__init__(**kwargs)
        self.load_from_library()
        self.filterManager = DictManager(itemDict=self.filterDict, possibleItems=measFilterList)

    #Overload [] to allow direct pulling of measurement filter info
    def __getitem__(self, filterName):
        return self.filterDict[filterName]

    def write_to_file(self,fileName=None):
        libFileName = fileName if fileName != None else self.libFile

        if libFileName:
            with open(libFileName, 'w') as FID:
                json.dump(self, FID, cls=LibraryCoders.LibraryEncoder, indent=2, sort_keys=True)

    def load_from_library(self):
        if self.libFile:
            try:
                with open(self.libFile, 'r') as FID:
                    tmpLib = json.load(FID, cls=LibraryCoders.LibraryDecoder)
                    if isinstance(tmpLib, MeasFilterLibrary):
                        #Update correlator filter lists to filter objects
                        for filt in tmpLib.filterDict.values():
                            if isinstance(filt, Correlator):
                                filterList = []
                                for f in filt.filters:
                                    filterList.append(tmpLib.filterDict[f])
                                filt.filters = filterList
                        self.filterDict.update(tmpLib.filterDict)
                        # grab library version
                        self.version = tmpLib.version
            except IOError:
                print("No measurement library found.")

    def json_encode(self, matlabCompatible=False):
        if matlabCompatible:
            return {label:filt for label,filt in self.filterDict.items() if filt.enabled}
        else:
            return {
                "filterDict": {label:filt for label,filt in self.filterDict.items()},
                "version": self.version
            }


measFilterList = [DigitalDemod, KernelIntegration, Correlator, StateComparator,
                  AlazarStreamSelector, X6StreamSelector,
                  Plotter, WriteToHDF5]

if __name__ == "__main__":

    #Work around annoying problem with multiple class definitions
    from MeasFilters import DigitalDemod, Correlator, MeasFilterLibrary

    testFilter1 = DigitalDemod(label='M1')
    testFilter2 = DigitalDemod(label='M2')
    testFilter3 = Correlator(label='M3')
    testFilter4 = Correlator(label='M4')
    filterDict = {'M1':testFilter1, 'M2':testFilter2, 'M3':testFilter3,'M4':testFilter4}

    testLib = MeasFilterLibrary(libFile='MeasFilterLibrary.json', filterDict=filterDict)

    with enaml.imports():
        from MeasFiltersViews import MeasFilterManagerWindow

    app = QtApplication()
    view = MeasFilterManagerWindow(filterLib=testLib)
    view.show()

    app.start()
