#! /usr/bin/env python
import h5py
from atom.api import Atom, Typed, Str, Bool, List

import enaml
from enaml.qt.qt_application import QtApplication

import argparse, sys

from instruments.InstrumentManager import InstrumentLibrary
from instruments import Digitizers
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
    errors = List()
    meta_file = Str()

    def __init__(self, **kwargs):
        super(ExpSettings, self).__init__(**kwargs)
        self.update_instr_list()

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
        """ Write all the libraries to their files. """

        if self.validate:
            self.errors = ExpSettingsVal.validate_lib()
            if self.errors != []:
                print("JSON Files did not validate")
                raise
        elif not self.validate:
            print "JSON Files validation disabled"
        self.channels.write_to_file()
        self.instruments.write_to_file()
        self.measurements.write_to_file()
        self.sweeps.write_to_file()

    def save_config(self,path):

        if self.validate:
            self.errors = ExpSettingsVal.validate_lib()
            if self.errors != []:
                print("JSON Files did not validate")
                raise
        elif not self.validate:
            print("JSON Files validation disabled")

        try:
            self.channels.write_to_file(fileName=path+ os.sep + os.path.basename(self.channels.libFile))
            self.measurements.write_to_file(fileName=path+ os.sep + os.path.basename(self.measurements.libFile))
            self.instruments.write_to_file(fileName=path+ os.sep + os.path.basename(self.instruments.libFile))
            self.sweeps.write_to_file(fileName=path+ os.sep + os.path.basename(self.sweeps.libFile))
            self.write_to_file(fileName=path+ os.sep + os.path.basename(self.curFileName))
        except Exception as e:
            self.errors.append(e.message)

    def load_config(self,path):
        self.clear_errors()

        print("LOADING FROM:",path)
        try:
            shutil.copy(path+ os.sep + os.path.basename(self.channels.libFile),self.channels.libFile)
            shutil.copy(path+ os.sep + os.path.basename(self.instruments.libFile),self.instruments.libFile)
            shutil.copy(path+ os.sep + os.path.basename(self.measurements.libFile),self.measurements.libFile)
            shutil.copy(path+ os.sep + os.path.basename(self.sweeps.libFile),self.sweeps.libFile)
            shutil.copy(path+ os.sep + os.path.basename(self.curFileName),self.curFileName)
        except Exception as e:
            self.errors.append(e.message)

    def load_meta(self):
        self.clear_errors()
        meta_file = self.meta_file
        if not os.path.isfile(meta_file):
            meta_file = config.AWGDir + os.sep + self.meta_file + '-meta.json'
        try:
            with open(meta_file, 'r') as FID:
                meta_info = json.load(FID)
        except IOError:
            self.errors.append('Meta info file not found')
            raise IOError
        # load sequence files into AWGs
        for awg in self.instruments.AWGs.displayList:
            self.instruments[awg].enabled = False
        for instr, seqFile in meta_info['instruments'].items():
            if instr not in self.instruments:
                self.errors.append("{} not found".format(instr))
                raise KeyError
            self.instruments[instr].seqFile = seqFile
            self.instruments[instr].enabled = True
            if hasattr(self.instruments[instr], 'parent'):
                self.instruments[self.instruments[instr].parent].enabled = True
        self.instruments.AWGs.update_display_list(None)

        # setup up digitizers with number of segments
        for instr in self.instruments.instrDict.values():
            if isinstance(instr, Digitizers.Digitizer) and hasattr(instr, 'nbrSegments'):
                instr.nbrSegments = meta_info['num_measurements']

        # setup a SegmentNum or SegmentNumWithCals sweep
        axis = meta_info['axis_descriptor'][0]
        cal_axes = [ax for ax in meta_info['axis_descriptor'] if ax['name'] == 'calibration']
        if len(cal_axes) > 0:
            sweep_name = 'SegmentNumWithCals'
            sweep_class = Sweeps.SegmentNumWithCals
            num_cals = sum(len(ax['points']) for ax in cal_axes)
        else:
            sweep_name = 'SegmentNum'
            sweep_class = Sweeps.SegmentNum
            num_cals = 0
        if sweep_name not in self.sweeps:
            sweep = sweep_class()
            self.sweeps.sweepDict[sweep_name] = sweep
            self.sweeps.sweepManager.update_display_list(None)
        else:
            sweep = self.sweeps[sweep_name]
        # set start/stop/step for viewing purposes
        sweep.start = axis['points'][0]
        sweep.stop = axis['points'][-1]
        sweep.numPoints = len(axis['points'])
        sweep.points = axis['points']
        sweep.usePointsList = True
        if num_cals > 0:
            sweep.numCals = num_cals
        if axis['unit']:
            sweep.axisLabel = "{} ({})".format(axis['name'], axis['unit'])
        else:
            sweep.axisLabel = axis['name']
        self.sweeps.sweepOrder = [sweep_name]

    def json_encode(self, matlabCompatible=True):
        #We encode this for an experiment settings file so no channels
        return {'instruments':self.instruments, 'sweeps':self.sweeps, 'measurements':self.measurements, 'CWMode':self.CWMode}

    def format_errors(self):
        return '\n'.join(self.errors)

    def clear_errors(self):
        del self.errors[:]

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
