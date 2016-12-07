"""
Measurement filters
"""

from atom.api import Atom, Int, Float, List, Str, Dict, Bool, Enum, Coerced, Typed, observe, Instance
import enaml
from enaml.qt.qt_application import QtApplication
from instruments.Digitizers import AlazarATS9870, X6
from DictManager import DictManager
import json
import sys
from JSONLibraryUtils import FileWatcher, LibraryCoders

class MeasFilter(Atom):
    label = Str()
    enabled = Bool(True)
    data_source = Str().tag(desc="Where the measurement data is pushed from.")

    def json_encode(self):
        jsonDict = self.__getstate__()
        jsonDict['x__class__'] = self.__class__.__name__
        jsonDict['x__module__'] = self.__class__.__module__

        obj = jsonDict.get('data_source', None)
        if obj and hasattr(obj, 'label'):
            jsonDict['data_source'] = obj.label
        return jsonDict

    def update_from_jsondict(self, jsonDict):
        jsonDict.pop('x__class__', None)
        jsonDict.pop('x__module__', None)

        #Convert the strings to ascii for Python 2
        if sys.version_info[0] < 3:
            for label,value in jsonDict.items():
                if hasattr(self, label):
                    if isinstance(value, unicode):
                        setattr(self, label, value.encode('ascii'))
                    else:
                        setattr(self, label, value)
        else:
            for label,value in jsonDict.items():
                if hasattr(self, label):
                    setattr(self, label, value)

class Plotter(MeasFilter):
    plot_mode = Enum('real', 'imag', 'amp/phase', 'real/imag', 'quad').tag(desc='Filtered data scope mode.')

class WriteToHDF5(MeasFilter):
    filename    = Str('').tag(desc='Path to file where records will be saved.')
    groupname   = Str('').tag(desc='Name of the root hdf5 group.')
    compression = Bool(True).tag(desc='Use gzip compression on the file.')

class Averager(MeasFilter):
    axis    = Str('').tag(desc='Name of the axis to average along.')

class AlazarStreamSelector(MeasFilter):
    data_source = Instance((str, AlazarATS9870))
    channel     = Int(1).tag(desc="Which channel to select from the Alazar")
    receiver    = True

class X6StreamSelector(MeasFilter):
    data_source                = Instance((str, X6))
    phys_channel               = Int(1).tag(desc="Which physical channel to select from the X6")
    dsp_channel                = Int(0).tag(desc="Which DSP channel to select from the X6")
    stream_type                = Enum('Raw', 'Demodulated', 'Integrated').tag(desc='Which stream type to select.')
    if_freq                    = Float(10e6).tag(desc='IF Frequency')
    kernel                     = Str("").tag(desc='Integration kernel vector')
    kernel_bias                = Str("").tag(desc="Kernel bias")
    threshold                  = Float(0.0).tag(desc='Qubit state decision threshold')
    threshold_invert           = Bool(False).tag(desc="Invert thresholder output")
    receiver                   = True

class Channelizer(MeasFilter):
    decimation_factor = Int(1).tag(desc="Decimation factor")
    frequency         = Float(10e6).tag(desc='The I.F. frequency for digital demodulation.')
    bandwidth         = Float(5e6).tag(desc='Low-pass filter bandwidth')

class KernelIntegrator(MeasFilter):
    kernel        = Str('').tag(desc="Integration kernel vector.")
    bias          = Float(0.0).tag(desc="Bias after integration.")
    simple_kernel = Bool(True)
    box_car_start = Float(1.0)
    box_car_stop  = Float(1.0)
    frequency     = Float(10e6)

class Correlator(MeasFilter):
    filters = List()

    def __init__(self, **kwargs):
        super(Correlator, self).__init__(**kwargs)
        if not self.filters:
            self.filters = [None, None]

    def json_encode(self):
        jsonDict = super(Correlator, self).json_encode()
        #For correlation filters return the filter list as a list of filter names
        filterList = jsonDict.pop('filters')
        jsonDict['filters'] = [item.label for item in filterList] if filterList else []
        jsonDict['data_source'] = ','.join(jsonDict['filters']) # correlator has mulitple data sources which are one and the same as the filter list
        return jsonDict

class StateComparator(MeasFilter):
    threshold        = Float(0.0)
    integration_time = Int(-1).tag(desc='Comparator integration time in decimated samples, use -1 for the entire record')

class MeasFilterLibrary(Atom):
    # filterDict = Dict(Str, MeasFilter)
    filterDict = Coerced(dict)
    libFile = Str().tag(transient=True)
    filterManager = Typed(DictManager)
    receivers = Typed(DictManager)
    version = Int(4)

    fileWatcher = Typed(FileWatcher.LibraryFileWatcher)

    def __init__(self, **kwargs):
        super(MeasFilterLibrary, self).__init__(**kwargs)
        self.load_from_library()
        if self.libFile:
            self.fileWatcher = FileWatcher.LibraryFileWatcher(
                self.libFile, self.load_from_library)
        self.filterManager = DictManager(
            itemDict=self.filterDict,
            possibleItems=measFilterList)
        self.receivers = DictManager(
            itemDict=self.filterDict,
            displayFilter=lambda x: hasattr(x, 'receiver'))

    #Overload [] to allow direct pulling of measurement filter info
    def __getitem__(self, filterName):
        return self.filterDict[filterName]

    def write_to_file(self,fileName=None):
        libFileName = fileName if fileName != None else self.libFile

        if libFileName:
            #Pause the file watcher to stop circular updating insanity
            if self.fileWatcher:
                self.fileWatcher.pause()

            with open(libFileName, 'w') as FID:
                json.dump(self, FID, cls=LibraryCoders.LibraryEncoder, indent=2, sort_keys=True)

            if self.fileWatcher:
                self.fileWatcher.resume()

    def load_from_library(self):
        if not self.libFile:
            return
        try:
            with open(self.libFile, 'r') as FID:
                tmpLib = json.load(FID, cls=LibraryCoders.LibraryDecoder)
            if not isinstance(tmpLib, MeasFilterLibrary):
                raise ValueError("Failed to load measurement library.")
            # Update correlator filter lists to filter objects
            for filt in tmpLib.filterDict.values():
                if isinstance(filt, Correlator):
                    filterList = []
                    for f in filt.filters:
                        filterList.append(tmpLib.filterDict[f])
                    filt.filters = filterList
            self.filterDict.update(tmpLib.filterDict)

            # delete removed items
            for filtName in list(self.filterDict.keys()):
                if filtName not in tmpLib.filterDict:
                    del self.filterDict[filtName]

            # grab library version
            self.version = tmpLib.version

            if self.filterManager:
                self.filterManager.update_display_list(None)
        except IOError:
            print("No measurement library found.")
        except ValueError:
            print("Failed to load measurement library.")

    def json_encode(self):
        return {
            "filterDict": {label:filt for label,filt in self.filterDict.items()},
            "version": self.version
        }


measFilterList = [Averager, Channelizer, KernelIntegrator, Correlator, StateComparator,
                  AlazarStreamSelector, X6StreamSelector,
                  Plotter, WriteToHDF5]

if __name__ == "__main__":

    #Work around annoying problem with multiple class definitions
    from MeasFilters import Channelizer, Correlator, MeasFilterLibrary

    M1 = Channelizer(label='M1')
    M2 = Channelizer(label='M2')
    M3 = Channelizer(label='M3')
    M12 = Correlator(label='M12', filters=[M1, M2])
    M123 = Correlator(label='M123', filters=[M1, M2, M3])
    filters = {'M1': M1,
               'M2': M2,
               'M3': M3,
               'M12': M12,
               'M123': M123}

    testLib = MeasFilterLibrary(libFile='MeasFilterLibrary.json',
                                filterDict=filters)

    with enaml.imports():
        from MeasFiltersViews import MeasFilterManagerWindow

    app = QtApplication()
    view = MeasFilterManagerWindow(filterLib=testLib)
    view.show()

    app.start()
