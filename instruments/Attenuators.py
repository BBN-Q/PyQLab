from atom.api import Str, Int, Float, Bool, Enum

from .Instrument import Instrument

class DigitalAttenuator(Instrument):
	ch1_attenuation = Float(0.0).tag(desc="Ch 1 attenuation (dB)")
	ch2_attenuation = Float(0.0).tag(desc="Ch 2 attenuation (dB)")
	ch3_attenuation = Float(0.0).tag(desc="Ch 3 attenuation (dB)")
