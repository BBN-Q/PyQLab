from traits.api import HasTraits, List, Instance, Str
import enaml
from enaml.stdlib.sessions import show_simple_view


from instruments.InstrumentManager import InstrumentLibrary
from instruments.MicrowaveSources import AgilentN51853A
from instruments.AWGs import APS

import json
import JSONHelpers

class ExpSettings(HasTraits):

    instrLib = Instance(InstrumentLibrary)
    sweeps = List()
    measurments = List()
    curFileName = Str('DefaultExpSettings.json', tranient=True)

    def load_from_file(self, fileName):
        pass

    def write_to_file(self):
        with open(self.curFileName,'w') as FID:
            json.dump(self, FID, cls=JSONHelpers.QLabEncoder)


if __name__ == '__main__':

    instruments = {}
    instruments['Agilent1'] = AgilentN51853A(name='Agilent1')
    instruments['Agilent2'] = AgilentN51853A(name='Agilent2')
    instruments['BBNAPS1'] = APS(name='BBNAPS1')
    instruments['BBNAPS2'] = APS(name='BBNAPS2')
    instrLib = InstrumentLibrary()
    instrLib.load_settings(instruments)

    expSettings= ExpSettings(instrLib=instrLib)

    with enaml.imports():
        from ExpSettingsView import ExpSettingsView

    show_simple_view(ExpSettingsView(expSettings=expSettings))





