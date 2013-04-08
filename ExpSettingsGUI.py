from traits.api import HasTraits, Instance, Str, Bool, on_trait_change
import enaml
from enaml.stdlib.sessions import show_simple_view

from instruments.InstrumentManager import InstrumentLibrary
import Sweeps
import MeasFilters

import json
import JSONHelpers

import config

class ExpSettings(HasTraits):

    sweeps = Instance(Sweeps.SweepLibrary)
    instruments = Instance(InstrumentLibrary)
    measurements = Instance(MeasFilters.MeasFilterLibrary)
    CWMode = Bool(False)
    curFileName = Str('DefaultExpSettings.json', transient=True)

    def __init__(self, **kwargs):
        super(ExpSettings, self).__init__(**kwargs)
        self.update_instr_list()

    @on_trait_change('instruments.instrDict_items')
    def update_instr_list(self):
        if self.sweeps:
            del self.sweeps.possibleInstrs[:]
            for key in self.instruments.instrDict.keys():
                self.sweeps.possibleInstrs.append(key)

    def load_from_file(self, fileName):
        pass

    def write_to_file(self):
        with open(self.curFileName,'w') as FID:
            json.dump(self, FID, cls=JSONHelpers.ScripterEncoder, indent=2, sort_keys=True, CWMode=self.CWMode)

if __name__ == '__main__':
    instrLib = InstrumentLibrary(libFile=config.instrumentLibFile)
    instrLib.load_from_library()

    sweepLib = Sweeps.SweepLibrary(libFile=config.sweepLibFile)
    sweepLib.load_from_library()

    filterLib = MeasFilters.MeasFilterLibrary(libFile=config.measurementLibFile)
    filterLib.load_from_library()

    from ExpSettingsGUI import ExpSettings
    expSettings= ExpSettings(sweeps=sweepLib, instruments=instrLib, measurements=filterLib)

    with enaml.imports():
        from ExpSettingsView import ExpSettingsView

    show_simple_view(ExpSettingsView(expSettings=expSettings))





