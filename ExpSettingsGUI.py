from traits.api import HasTraits, List, Instance, Str
import enaml
from enaml.stdlib.sessions import show_simple_view


from instruments.InstrumentManager import InstrumentLibrary
from instruments.MicrowaveSources import AgilentN51853A
from instruments.AWGs import APS
import Sweeps
import MeasFilters

import json
import JSONHelpers

class ExpSettings(HasTraits):

    instruments = Instance(InstrumentLibrary)
    sweeps = List()
    measurements = List()
    curFileName = Str('DefaultExpSettings.json', transient=True)

    def load_from_file(self, fileName):
        pass

    def write_to_file(self):
        with open(self.curFileName,'w') as FID:
            json.dump(self, FID, cls=JSONHelpers.QLabEncoder, indent=2, sort_keys=True)


if __name__ == '__main__':

    instruments = {}
    instruments['Agilent1'] = AgilentN51853A(name='Agilent1')
    instruments['Agilent2'] = AgilentN51853A(name='Agilent2')
    instruments['BBNAPS1'] = APS(name='BBNAPS1')
    instruments['BBNAPS2'] = APS(name='BBNAPS2')
    instrLib = InstrumentLibrary(instrDict=instruments)

    testSweep1 = Sweeps.Frequency(name='TestSweep1', start=5, stop=6, step=0.1, instr=instruments['Agilent1'])
    testSweep2 = Sweeps.Power(name='TestSweep2', start=-20, stop=0, step=0.5, instr=instruments['Agilent2'])

    testFilter1 = MeasFilters.DigitalHomodyne(name='M1', boxCarStart=100, boxCarStop=500, IFfreq=10e6, samplingRate=250e6)
    testFilter2 = MeasFilters.DigitalHomodyne(name='M2', boxCarStart=150, boxCarStop=600, IFfreq=39.2e6, samplingRate=250e6)

    expSettings= ExpSettings(instruments=instrLib, sweeps=[testSweep1, testSweep2], measurements=[testFilter1, testFilter2])

    with enaml.imports():
        from ExpSettingsView import ExpSettingsView

    show_simple_view(ExpSettingsView(expSettings=expSettings))





