from atom.api import Str, Int, Float, Bool, Enum

from .Instrument import Instrument

class DigitalAttenuator(Instrument):
	ch1Attenuation = Float(0.0).tag(desc="Ch 1 attenuation (dB)")
	ch2Attenuation = Float(0.0).tag(desc="Ch 2 attenuation (dB)")
	ch3Attenuation = Float(0.0).tag(desc="Ch 3 attenuation (dB)")
