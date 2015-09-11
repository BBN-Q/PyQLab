from atom.api import (Atom, Str, List, Dict, Property, Typed, Unicode, Coerced, Int)
import json, enaml
from enaml.qt.qt_application import QtApplication

from Instrument import Instrument
import MicrowaveSources
import AWGs
import FileWatcher

import importlib

from DictManager import DictManager

import Digitizers, Analysers, DCSources, Attenuators

from plugins import find_plugins

newOtherInstrs = [Digitizers.AlazarATS9870,
    Digitizers.X6,
    Analysers.HP71000,
    Analysers.SpectrumAnalyzer,
    DCSources.YokoGS200,
    Attenuators.DigitalAttenuator]

plugins = find_plugins(Digitizers.Digitizer)
for plugin in plugins:
    newOtherInstrs.append(plugin)
    globals().update({plugin.__name__: plugin})
    print 'Registered Digitizer Driver {0}'.format(plugin.__name__)


class InstrumentLibrary(Atom):
    #All the instruments are stored as a dictionary keyed of the instrument name
    instrDict = Dict()
    libFile = Str().tag(transient=True)

    #Some helpers to manage types of instruments
    AWGs = Typed(DictManager)
    sources = Typed(DictManager)
    others = Typed(DictManager)
    version = Int(0)

    fileWatcher = Typed(FileWatcher.LibraryFileWatcher)

    def __init__(self, **kwargs):
        super(InstrumentLibrary, self).__init__(**kwargs)
        self.load_from_library()
        if self.libFile:
            self.fileWatcher = FileWatcher.LibraryFileWatcher(self.libFile, self.update_from_file)

        #Setup the dictionary managers for the different instrument types
        self.AWGs = DictManager(itemDict=self.instrDict,
                                displayFilter=lambda x: isinstance(x, AWGs.AWG),
                                possibleItems=AWGs.AWGList)
        
        self.sources = DictManager(itemDict=self.instrDict,
                                   displayFilter=lambda x: isinstance(x, MicrowaveSources.MicrowaveSource),
                                   possibleItems=MicrowaveSources.MicrowaveSourceList)

        self.others = DictManager(itemDict=self.instrDict,
                                  displayFilter=lambda x: not isinstance(x, AWGs.AWG) and not isinstance(x, MicrowaveSources.MicrowaveSource),
                                  possibleItems=newOtherInstrs)

    #Overload [] to allow direct pulling out of an instrument
    def __getitem__(self, instrName):
        return self.instrDict[instrName]

    def write_to_file(self,fileName=None):
        #Move import here to avoid circular import
        import JSONHelpers
        libFileName = fileName if fileName != None else self.libFile
        if self.libFile:
            #Pause the file watcher to stop circular updating insanity
            if self.fileWatcher:
                self.fileWatcher.pause()
                
                if libFileName:
                    with open(libFileName, 'w') as FID:
                        json.dump(self, FID, cls=JSONHelpers.LibraryEncoder, indent=2, sort_keys=True)
            
            if self.fileWatcher:
                self.fileWatcher.resume()

    def load_from_library(self):
        #Move import here to avoid circular import
        import JSONHelpers
        if self.libFile:
            try:
                with open(self.libFile, 'r') as FID:
                    tmpLib = json.load(FID, cls=JSONHelpers.LibraryDecoder)
                    if isinstance(tmpLib, InstrumentLibrary):
                        self.instrDict.update(tmpLib.instrDict)
                        # grab library version
                        self.version = tmpLib.version
            except IOError:
                print('No instrument library found')
            except ValueError:
                print('Failed to load instrument library')

    def update_from_file(self):
        """
        Only update relevant parameters
        Helps avoid stale references by replacing whole channel objects as in load_from_library
        and the overhead of recreating everything.
        """
        if self.libFile:
            with open(self.libFile, 'r') as FID:
                try:
                    allParams = json.load(FID)['instrDict']
                except ValueError:
                    print('Failed to update instrument library from file.  Probably just half-written.')
                    return

                # update and add new items
                for instrName, instrParams in allParams.items():
                    # Re-encode the strings as ascii (this should go away in Python 3)
                    instrParams = {k.encode('ascii'):v for k,v in instrParams.items()}
                    # update
                    if instrName in self.instrDict:
                        self.instrDict[instrName].update_from_jsondict(instrParams)
                    else:
                        # load class from name and update from json
                        className = instrParams['x__class__']
                        moduleName = instrParams['x__module__']

                        mod = importlib.import_module(moduleName)
                        cls = getattr(mod, className)
                        self.instrDict[instrName]  = cls()
                        self.instrDict[instrName].update_from_jsondict(instrParams)

                # delete removed items
                for instrName in self.instrDict.keys():
                    if instrName not in allParams:
                        del self.instrDict[instrName]

    def json_encode(self, matlabCompatible=False):
        #When serializing for matlab return only enabled instruments, otherwise all
        if matlabCompatible:
            return {label:instr for label,instr in self.instrDict.items() if instr.enabled}
        else:
            return {
                "instrDict": {label:instr for label,instr in self.instrDict.items()},
                "version": self.version
            }


if __name__ == '__main__':

    
    from MicrowaveSources import AgilentN5183A
    instrLib = InstrumentLibrary(instrDict={'Agilent1':AgilentN5183A(label='Agilent1'), 'Agilent2':AgilentN5183A(label='Agilent2')})
    with enaml.imports():
        from InstrumentManagerView import InstrumentManagerWindow

    app = QtApplication()
    view = InstrumentManagerWindow(instrLib=instrLib)
    view.show()
    app.start()
