from traits.api import Str, Int, Float, Bool, Enum

from Instrument import Instrument

class DCSource(Instrument):
	output = Bool(False, desc='Output enabled')
	mode = Enum('voltage', 'current', desc='Output mode (current or voltage source)')
	value = Float(0.0, desc='Output value (current or voltage)')

class YokoGS200(DCSource):
	outputRange = Enum(1e-3, 10e-3, 100e-3, 200e-3, 1, 10, 30, desc='Output range')