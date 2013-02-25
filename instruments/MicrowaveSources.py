from traits.api import Str, Int, Float, Bool, Enum
# from traitsui.api import View, Item, VGroup, HGroup, Group, spring

import enaml
from enaml.stdlib.sessions import show_simple_view
from enaml.qt.qt_application import QtApplication

from Instrument import Instrument

class MicrowaveSource(Instrument):
    name = Str
    address = Str('', desc='address of unit as GPIB or I.P.', label='Address')
    power = Float(0.0, desc='output power in dBm', label='Output Power')
    frequency = Float(5.0, desc='frequency in GHz', label='Frequency')
    modulate = Bool(False, desc='whether output is modulated', label='Modulate')
    alc = Bool(False, desc='whether automatic level control is on', label='ALC')
    pulseModulate = Bool(False, desc='whether pulse modulation is on', label='Pulse Mod.')
    pulseModSource = Enum('Internal', 'External', desc='source of pulse modulation', label='Pulse Mod. Source')


class AgilentN51853A(MicrowaveSource):
    pass

class HS9000(MicrowaveSource):
    pass

class LabBrick(MicrowaveSource):
    pass

#List of possible sources for other views
MicrowaveSourceList = [AgilentN51853A, HS9000, LabBrick]

if __name__ == "__main__":
    uwSource = AgilentN51853A(name='Agilent1')
    with enaml.imports():
        from MicrowaveSourcesView import MicrowaveSourceView

    session = show_simple_view(MicrowaveSourceView(uwSource=uwSource))
