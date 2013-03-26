from traits.api import HasTraits, List, Instance, Str, on_trait_change
import enaml
from enaml.stdlib.sessions import show_simple_view


from instruments.InstrumentManager import InstrumentLibrary
from instruments.MicrowaveSources import AgilentN51853A
from instruments.AWGs import APS
from instruments.Digitizers import AlazarATS9870
import Sweeps
import MeasFilters

import json
import JSONHelpers

class ExpSettings(HasTraits):

    sweeps = Instance(Sweeps.SweepLibrary)
    instruments = Instance(InstrumentLibrary)
    measurements = Instance(MeasFilters.MeasFilterLibrary)
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
            json.dump(self, FID, cls=JSONHelpers.ScripterEncoder, indent=2, sort_keys=True)

if __name__ == '__main__':
    # instruments = {}
    # instruments['Agilent1'] = AgilentN51853A(name='Agilent1')
    # instruments['Agilent2'] = AgilentN51853A(name='Agilent2')
    # instruments['BBNAPS1'] = APS(name='BBNAPS1')
    # instruments['BBNAPS2'] = APS(name='BBNAPS2')
    # instruments['scope'] = AlazarATS9870(name='scope')
    instrLib = InstrumentLibrary(libFile='InstrumentLibrary.json')
    instrLib.load_from_library()

    sweepLib = Sweeps.SweepLibrary(libFile='SweepLibrary.json')
    sweepLib.load_from_library()

    # testFilter1 = MeasFilters.DigitalHomodyne(name='M1', boxCarStart=100, boxCarStop=500, IFfreq=10e6, samplingRate=250e6)
    # testFilter2 = MeasFilters.DigitalHomodyne(name='M2', boxCarStart=150, boxCarStop=600, IFfreq=39.2e6, samplingRate=250e6)
    filterLib = MeasFilters.MeasFilterLibrary(libFile='MeasFilterLibrary.json')
    filterLib.load_from_library()

    from ExpSettingsGUI import ExpSettings
    expSettings= ExpSettings(sweeps=sweepLib, instruments=instrLib, measurements=filterLib)

    with enaml.imports():
        from ExpSettingsView import ExpSettingsView

    show_simple_view(ExpSettingsView(expSettings=expSettings))





