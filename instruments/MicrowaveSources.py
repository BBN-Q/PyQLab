from atom.api import Atom, Float, Enum, Bool

import enaml
from enaml.qt.qt_application import QtApplication

from .Instrument import Instrument

class MicrowaveSource(Instrument):
    power = Float(0.0).tag(desc="Output power in dBm")
    frequency = Float(5.0).tag(desc="Frequency in GHz")
    output = Bool(False).tag(desc="Whether the output is on")
    mod = Bool(False).tag(desc="Whether output is modulated")
    alc = Bool(False).tag(desc="Whether automatic level control is on")
    pulse = Bool(False).tag(desc="Whether pulse modulation is on")
    pulse_source = Enum("Internal", "External").tag(desc="Source of pulse modulation")

    #For blanking the source we need to know the maximum rate and the delay
    gate_buffer = Float(0.0).tag(desc="How much extra time should be added onto the beginning of the gating pulse")
    gate_min_width = Float(0.0).tag(desc="The minimum gating pulse width")
    gate_delay = Float(0.0).tag(desc="How the gating pulse should be shifted")

class N5183A(MicrowaveSource):
    gate_buffer = Float(20e-9)
    gate_min_width = Float(100e-9)
    gate_delay = Float(-60e-9)

class HS9000(MicrowaveSource):
    gate_buffer = Float(20e-9)
    gate_min_width = Float(100e-9)
    gate_delay = Float(-60e-9)

class Labbrick(MicrowaveSource):
    ref_source = Enum("Internal" , "External").tag(desc="Source of 10MHz ref.")

    gate_buffer = Float(20e-9)
    gate_min_width = Float(100e-9)
    gate_delay = Float(-60e-9)

class SMIQ03(MicrowaveSource):
    ref_source = Enum("Internal" , "External").tag(desc="Source of 10MHz ref.")
    gate_buffer = Float(20e-9)
    gate_min_width = Float(100e-9)
    gate_delay = Float(-60e-9)

class BNC845(MicrowaveSource):
    ref_source = Enum("Internal" , "External").tag(desc="Source of 10MHz ref.")
    gate_buffer = Float(20e-9)
    gate_min_width = Float(100e-9)
    gate_delay = Float(-60e-9)

class HP8673B(MicrowaveSource):
    pass

class HP8340B(MicrowaveSource):
    pass

#List of possible sources for other views
MicrowaveSourceList = [N5183A, HS9000, Labbrick, SMIQ03, HP8673B, HP8340B, BNC845]

if __name__ == "__main__":
    from MicrowaveSources import N5183A
    mySource = N5183A(label="Agilent1")
    with enaml.imports():
        from MicrowaveSourcesViews import MicrowaveSourceView

    #TODO: hook into iPython's event loop
    app = QtApplication()
    view = MicrowaveSourceView(uwSource=mySource)
    view.show()
    app.start()
