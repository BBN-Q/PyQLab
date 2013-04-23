from traits.api import HasTraits, List, Instance, Float, Dict, Str, Property, on_trait_change

import json

from Instrument import Instrument
import MicrowaveSources
import AWGs

class InstrumentLibrary(HasTraits):
    #All the instruments are stored as a dictionary keyed of the instrument name
    instrDict = Dict(Str, Instrument)
    libFile = Str(transient=True)

    #Some helpers to pull out certain types of instruments
    AWGs = Property(List, depends_on='instrDict[]')
    sources = Property(List, depends_on='instrDict[]')

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

    #Getter for AWG list
    def _get_AWGs(self):
        return sorted([instr for instr in self.instrDict.values() if isinstance(instr, AWGs.AWG)], key = lambda instr : instr.name)

    #Getter for microwave source list
    def _get_sources(self):
        return sorted([instr for instr in self.instrDict.values() if isinstance(instr, MicrowaveSources.MicrowaveSource)], key = lambda instr : instr.name)

if __name__ == '__main__':
    import enaml
    from enaml.stdlib.sessions import show_simple_view

    from Libraries import instrumentLib
    with enaml.imports():
        from InstrumentManagerView import InstrumentManagerWindow
    show_simple_view(InstrumentManagerWindow(instrLib=instrumentLib))








    
    
