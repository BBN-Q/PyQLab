from atom.api import Str, Int, Float, Bool, Enum

from .Instrument import Instrument

class DCSource(Instrument):
	output = Bool(False).tag(desc='Output enabled')
	mode = Enum('voltage', 'current').tag(desc='Output mode (current or voltage source)')
	value = Float(0.0).tag(desc='Output value (current or voltage)')

class YokogawaGS200(DCSource):
	output_range = Enum(1e-3, 10e-3, 100e-3, 200e-3, 1, 10, 30).tag(desc='Output range')

	def json_encode(self):
		return super(YokogawaGS200, self).json_encode()
