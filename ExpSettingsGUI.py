#! /usr/bin/env python
import h5py
from atom.api import Atom, Typed, Str, Bool, List

import enaml
from enaml.qt.qt_application import QtApplication

import argparse, sys

from instruments.InstrumentManager import InstrumentLibrary
import Sweeps
import MeasFilters
import QGL.ChannelLibrary
import QGL.Channels
import json
import os
import config
import ExpSettingsVal
from DictManager import DictManager
import shutil

class ExpSettings(Atom):

    sweeps = Typed(Sweeps.SweepLibrary)
    instruments = Typed(InstrumentLibrary)
    measurements = Typed(MeasFilters.MeasFilterLibrary)
    channels = Typed(QGL.ChannelLibrary.ChannelLibrary)
    logicalChannelManager = Typed(DictManager)
    physicalChannelManager = Typed(DictManager)
    CWMode = Bool(False)
    validate = Bool(True)
    curFileName = Str('DefaultExpSettings.json')
    validation_errors = List()

    def __init__(self, **kwargs):
        super(ExpSettings, self).__init__(**kwargs)
        self.update_instr_list()
        self.validation_errors = []

        # setup on change AWG
        self.instruments.AWGs.onChangeDelegate = self.channels.on_awg_change
        # link adding AWG to auto-populating channels
        self.instruments.AWGs.populate_physical_channels = lambda awg : self.populate_physical_channels(awg)

        self.logicalChannelManager = DictManager(
            itemDict = self.channels.channelDict,
            displayFilter = lambda x : isinstance(x, QGL.Channels.LogicalChannel),
            possibleItems = QGL.Channels.NewLogicalChannelList
        )
        self.physicalChannelManager = DictManager(
            itemDict = self.channels.channelDict,
            displayFilter = lambda x : isinstance(x, QGL.Channels.PhysicalChannel),
            possibleItems = QGL.Channels.NewPhysicalChannelList,
            otherActions = {"Auto": self.populate_physical_channels}
        )

    # TODO: get this to work
    # @on_trait_change('instruments.instrDict_items')
    def update_instr_list(self):
        if self.sweeps:
            del self.sweeps.possibleInstrs[:]
            for key in self.instruments.instrDict.keys():
                self.sweeps.possibleInstrs.append(key)

    def load_from_file(self, fileName):
        pass

    def write_to_file(self,fileName=None):
        curFileName = fileName if fileName != None else self.curFileName
        with open(curFileName, 'w') as FID:
            json.dump(self, FID, cls=ScripterEncoder, indent=2, sort_keys=True, CWMode=self.CWMode)

    def write_libraries(self):
        """Write all the libraries to their files.

        """

        if self.validate:
            self.validation_errors = ExpSettingsVal.validate_lib()
            if self.validation_errors != []:
                print "JSON Files did not validate"
                return False
        elif not self.validate:
            print "JSON Files validation disabled"
        self.channels.write_to_file()
        self.instruments.write_to_file()
        self.measurements.write_to_file()
        self.sweeps.write_to_file()

        return True

    def save_config(self,path):

        if self.validate:
            self.validation_errors = ExpSettingsVal.validate_lib()
            if self.validation_errors != []:
                print "JSON Files did not validate"
                return False
        elif not self.validate:
            print "JSON Files validation disabled"

        try:
            self.channels.write_to_file(fileName=path+ os.sep + os.path.basename(self.channels.libFile))
            self.measurements.write_to_file(fileName=path+ os.sep + os.path.basename(self.measurements.libFile))
            self.instruments.write_to_file(fileName=path+ os.sep + os.path.basename(self.instruments.libFile))
            self.sweeps.write_to_file(fileName=path+ os.sep + os.path.basename(self.sweeps.libFile))
            self.write_to_file(fileName=path+ os.sep + os.path.basename(self.curFileName))
        except:
            return False


        return True

    def load_config(self,path):

        print("LOADING FROM:",path)

        try:
            shutil.copy(path+ os.sep + os.path.basename(self.channels.libFile),self.channels.libFile)
            shutil.copy(path+ os.sep + os.path.basename(self.instruments.libFile),self.instruments.libFile)
            shutil.copy(path+ os.sep + os.path.basename(self.measurements.libFile),self.measurements.libFile)
            shutil.copy(path+ os.sep + os.path.basename(self.sweeps.libFile),self.sweeps.libFile)
            shutil.copy(path+ os.sep + os.path.basename(self.curFileName),self.curFileName)
        except shutil.Error as e:
            print('Error: %s' % e)
        except IOError as e:
            print('Error: %s' % e.strerror)

        return True


    def apply_quickpick(self, name):
        try:
            with open(config.quickpickFile, 'r') as FID:
                quickPicks = json.load(FID)
        except IOError:
            print('No quick pick file found.')
            return

        quickPick = quickPicks[name]

        #Apply sequence name
        if 'seqFile' in quickPick and 'seqDir' in quickPick:
            for awgName in self.instruments.AWGs.displayList:
                self.instruments[awgName].seqFile = os.path.normpath(os.path.join(config.AWGDir, quickPick['seqDir'],
                                 '{}-{}{}'.format(quickPick['seqFile'], awgName, self.instruments[awgName].seqFileExt)))

        #Apply sweep info
        if 'sweeps' in quickPick:
            for sweep in quickPick['sweeps']:
                if sweep in self.sweeps.sweepDict:
                    for k,v in quickPick['sweeps'][sweep].items():
                        setattr(self.sweeps.sweepDict[sweep], k, v)
        if 'sweepOrder' in quickPick:
            self.sweeps.sweepOrder = quickPick['sweepOrder']

        #Setup the digitizer number of segments
        if 'nbrSegments' in quickPick:
            self.instruments['scope'].nbrSegments = quickPick['nbrSegments']

    def json_encode(self, matlabCompatible=True):
        #We encode this for an experiment settings file so no channels
        return {'instruments':self.instruments, 'sweeps':self.sweeps, 'measurements':self.measurements, 'CWMode':self.CWMode}

    def format_errors(self):
        return '\n'.join(self.validation_errors)

    def populate_physical_channels(self, awgs=None):
        import instruments.AWGs
        if awgs == None:
            awgs = filter(lambda x: isinstance(x, instruments.AWGs.AWG), self.instruments.instrDict.values())
        for awg in awgs:
            channels = awg.get_naming_convention()
            for ch in channels:
                label = awg.label + '-' + ch
                if label in self.channels:
                    continue
                # TODO: less kludgy lookup of appropriate channel type
                if 'm' in ch.lower():
                    pc = QGL.Channels.PhysicalMarkerChannel()
                else:
                    pc = QGL.Channels.PhysicalQuadratureChannel()
                pc.label = label
                pc.AWG = awg.label
                pc.translator = awg.translator
                pc.samplingRate = awg.samplingRate
                self.channels[label] = pc
        self.physicalChannelManager.update_display_list(None)


class ScripterEncoder(json.JSONEncoder):
    """
    Helper for QLab to encode all the classes for the matlab experiment script.
    """
    def __init__(self, CWMode=False, **kwargs):
        super(ScripterEncoder, self).__init__(**kwargs)
        self.CWMode = CWMode

    def default(self, obj):
        if isinstance(obj, Atom):
            #Check for a json_encode option
            try:
                jsonDict = obj.json_encode(matlabCompatible=True)
            except AttributeError:
                jsonDict = obj.__getstate__()
            except:
                print("Unexpected error encoding to JSON")
                raise

            #Patch up some issues on the JSON dictionary
            #Matlab doesn't use the label
            jsonDict.pop('label', None)

            return jsonDict

        else:
            return super(ScripterEncoder, self).default(obj)

if __name__ == '__main__':
    import Libraries

    from ExpSettingsGUI import ExpSettings
    expSettings = ExpSettings(sweeps=Libraries.sweepLib,
                              instruments=Libraries.instrumentLib,
                              measurements=Libraries.measLib,
                              channels=QGL.ChannelLibrary.channelLib)

    # setup on change AWG
    # TODO: isn't this already handled byteh ExpSettings constructor?
    expSettings.instruments.AWGs.onChangeDelegate = expSettings.channels.on_awg_change

    #If we were passed a scripter file to write to then use it
    parser = argparse.ArgumentParser()
    parser.add_argument('--scripterFile', action='store', dest='scripterFile', default=None)
    options =  parser.parse_args(sys.argv[1:])
    if options.scripterFile:
        expSettings.curFileName = options.scripterFile

    with enaml.imports():
        from ExpSettingsView import ExpSettingsView

    app = QtApplication()
    view = ExpSettingsView(expSettings=expSettings)
    view.show()
    app.start()
