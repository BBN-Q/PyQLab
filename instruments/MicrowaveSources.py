from traits.api import Str, Int, Float, Bool, Enum

import enaml
from enaml.stdlib.sessions import show_simple_view

from Instrument import Instrument

class MicrowaveSource(Instrument):
    address = Str('', desc='Address of unit as GPIB or I.P.')
    power = Float(0.0, desc='Output power in dBm')
    frequency = Float(5.0, desc='Frequency in GHz')
    modulate = Bool(False, desc='Whether output is modulated')
    alc = Bool(False, desc='Whether automatic level control is on')
    pulseModulate = Bool(False, desc='Whether pulse modulation is on')
    pulseModSource = Enum('Internal', 'External', desc='Source of pulse modulation')


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
