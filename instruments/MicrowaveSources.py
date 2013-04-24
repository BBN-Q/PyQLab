from traits.api import Str, Int, Float, Bool, Enum

import enaml
from enaml.stdlib.sessions import show_simple_view

from Instrument import Instrument

class MicrowaveSource(Instrument):
    address = Str('', desc='Address of unit as GPIB or I.P.')
    power = Float(0.0, desc='Output power in dBm')
    frequency = Float(5.0, desc='Frequency in GHz')
    output = Bool(False, desc='Whether the output is on.')
    mod = Bool(False, desc='Whether output is modulated')
    alc = Bool(False, desc='Whether automatic level control is on')
    pulse = Bool(False, desc='Whether pulse modulation is on')
    pulseSource = Enum('Internal', 'External', desc='Source of pulse modulation')

    #For blanking the source we need to know the maximum rate and the delay
    gateBuffer = Float(0.0)
    gateMinWidth = Float(0.0)
    gateDelay = Float(0.0)

class AgilentN5183A(MicrowaveSource):
    gateBuffer = Float(20e-9)
    gateMinWidth = Float(100e-9)
    gateDelay = Float(-60e-9)

class HolzworthHS9000(MicrowaveSource):
    gateBuffer = Float(20e-9)
    gateMinWidth = Float(100e-9)
    gateDelay = Float(-60e-9)

class Labbrick(MicrowaveSource):
    refSource = Enum('Internal' , 'External', desc='Source of 10MHz ref.')

    gateBuffer = Float(20e-9)
    gateMinWidth = Float(100e-9)
    gateDelay = Float(-60e-9)

class Labbrick64(MicrowaveSource):
    gateBuffer = Float(20e-9)
    gateMinWidth = Float(100e-9)
    gateDelay = Float(-60e-9)

class HP8673B(MicrowaveSource):
    pass

class HP8340B(MicrowaveSource):
    pass

#List of possible sources for other views
MicrowaveSourceList = [AgilentN5183A, HolzworthHS9000, Labbrick, Labbrick64, HP8673B, HP8340B]

if __name__ == "__main__":
    from MicrowaveSources import AgilentN5183A
    uwSource = AgilentN5183A(name='Agilent1')
    with enaml.imports():
        from MicrowaveSourcesView import MicrowaveSourceView

    session = show_simple_view(MicrowaveSourceView(uwSource=uwSource))
