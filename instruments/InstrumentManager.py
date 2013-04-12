from traits.api import HasTraits, List, Instance, Float, Dict, Str, Property, on_trait_change
import enaml
from enaml.stdlib.sessions import show_simple_view

import json

from Instrument import Instrument
from MicrowaveSources import MicrowaveSourceList, MicrowaveSource
from AWGs import AWGList, AWG

class InstrumentLibrary(HasTraits):
    #All the instruments are stored as a dictionary keyed of the instrument name
    instrDict = Dict(Str, Instrument)
    libFile = Str(transient=True)

    def __init__(self, **kwargs):
        super(InstrumentLibrary, self).__init__(**kwargs)
        self.load_from_library()

    #Overload [] to allow direct pulling of channel info
    def __getitem__(self, instrName):
        return self.instrDict[instrName]

    @on_trait_change('instrDict.anytrait')
    def write_to_library(self):
        #Move import here to avoid circular import
        import JSONHelpers
        if self.libFile:
            try:
                with open(self.libFile,'w') as FID:
                    json.dump(self, FID, cls=JSONHelpers.LibraryEncoder, indent=2, sort_keys=True)
            except IOError:
                print('Failed to write to instrument library.')
            else:
                pass
                # print('Something went horribly wrong: writing empty instrument library.')
                # #If things go wrong, dump an empty dictionary so the file isn't corrupted
                # with open(self.libFile,'w') as FID:
                #     json.dump({}, FID)
                # import pdb; pdb.set_trace()

    def load_from_library(self):
        #Move import here to avoid circular import
        import JSONHelpers
        if self.libFile:
            try:
                with open(self.libFile, 'r') as FID:
                    tmpLib = json.load(FID, cls=JSONHelpers.LibraryDecoder)
                    if isinstance(tmpLib, InstrumentLibrary):
                        self.instrDict.update(tmpLib.instrDict)
            except IOError:
                print('No instrument library found')
            except ValueError:
                print('Failed to load instrument library')

if __name__ == '__main__':
    from MicrowaveSources import AgilentN5183A
    from AWGs import APS
    from Digitizers import AlazarATS9870
    from InstrumentManager import InstrumentLibrary
    instruments = {}
    instruments['Agilent1'] = AgilentN5183A(name='Agilent1')
    instruments['Agilent2'] = AgilentN5183A(name='Agilent2')
    instruments['BBNAPS1'] = APS(name='BBNAPS1')
    instruments['BBNAPS2'] = APS(name='BBNAPS2')
    instruments['scope'] = AlazarATS9870(name='scope')
    instrLib = InstrumentLibrary(instrDict=instruments, libFile='InstrumentLibrary.json')
    with enaml.imports():
        from InstrumentManagerView import InstrumentManagerWindow
    show_simple_view(InstrumentManagerWindow(instrLib=instrLib))








    
    
