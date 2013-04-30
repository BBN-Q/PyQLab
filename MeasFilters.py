"""
Measurement filters
"""

from traits.api import HasTraits, Int, Float, List, Str, Dict, Bool, on_trait_change, Either
import enaml

import json

class MeasFilter(HasTraits):
    name = Str
    channel = Int(1)
    enabled = Bool(True)
    plotScope = Bool(False, desc='Whether to show the raw data scope.')

    def json_encode(self, matlabCompatible=False):
        jsonDict = self.__getstate__()
        if matlabCompatible:
            jsonDict['filterType'] = self.__class__.__name__
            jsonDict.pop('enabled', None)
            jsonDict.pop('name', None)
        else:
            jsonDict['__class__'] = self.__class__.__name__
            jsonDict['__module__'] = self.__class__.__module__
        return jsonDict

class DigitalHomodyne(MeasFilter):
    boxCarStart = Int(0, desc='The start index of the integration window in pts.')
    boxCarStop = Int(0, desc='The stop index of the integration window in pts.')
    IFfreq = Float(10e6, desc='The I.F. frequency for digital demodulation.')
    samplingRate = Float(250e6, desc='The sampling rate of the digitizer.')
    phase = Float(0.0, desc='Phase rotation to apply in rad.')

class Correlator(MeasFilter):
    filters = Either(List(MeasFilter), List(Str))

    def json_encode(self, matlabCompatible=False):
        jsonDict = super(Correlator, self).json_encode(matlabCompatible)
        #For correlation filters return the filter list as a list of filter names
        filterList = jsonDict.pop('filters')
        jsonDict['filters'] = [item.name for item in filterList]
        jsonDict.pop('channel')
        jsonDict.pop('plotScope')
        return jsonDict

class MeasFilterLibrary(HasTraits):
    filterDict = Dict(Str, MeasFilter)
    libFile = Str(transient=True)
    filterList = List([DigitalHomodyne, Correlator], transient=True)

    def __init__(self, **kwargs):
        super(MeasFilterLibrary, self).__init__(**kwargs)
        self.load_from_library()

    #Overload [] to allow direct pulling of measurement filter info
    def __getitem__(self, filterName):
        return self.filterDict[filterName]

    @on_trait_change('filterDict.anytrait')
    def write_to_library(self):
        #Move import here to avoid circular import
        import JSONHelpers
        if self.libFile:
            with open(self.libFile,'w') as FID:
                json.dump(self, FID, cls=JSONHelpers.LibraryEncoder, indent=2, sort_keys=True)

    def load_from_library(self):
        import JSONHelpers
        if self.libFile:
            try:
                with open(self.libFile, 'r') as FID:
                    tmpLib = json.load(FID, cls=JSONHelpers.LibraryDecoder)
                    if isinstance(tmpLib, MeasFilterLibrary):
                        #Update correlator filter lists to filter objects
                        for filt in tmpLib.filterDict.values():
                            if isinstance(filt, Correlator):
                                filterList = []
                                for f in filt.filters:
                                    filterList.append(tmpLib.filterDict[f])
                                filt.filters = filterList
                        self.filterDict.update(tmpLib.filterDict)
            except IOError:
                print("No measurement library found.")

if __name__ == "__main__":

    #Work around annoying problem with multiple class definitions 
    from MeasFilters import DigitalHomodyne, MeasFilterLibrary

    testFilter1 = DigitalHomodyne(name='M1', boxCarStart=100, boxCarStop=500, IFfreq=10e6, samplingRate=250e6, channel=1)
    testFilter2 = DigitalHomodyne(name='M2', boxCarStart=150, boxCarStop=600, IFfreq=39.2e6, samplingRate=250e6, channel=2)

    testLib = MeasFilterLibrary(libFile='MeasFilterLibrary.json')
    testLib.filterDict.update({'M1':testFilter1, 'M2':testFilter2})
    from enaml.stdlib.sessions import show_simple_view
    with enaml.imports():
        from MeasFiltersViews import MeasFilterManagerWindow
    session = show_simple_view(MeasFilterManagerWindow(filterLib=testLib))
