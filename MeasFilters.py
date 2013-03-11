"""
Measurement filters
"""

from traits.api import HasTraits, Int, Float, List, Str

class MeasFilter(HasTraits):
	name = Str
	channel = Int

class DigitalHomodyne(MeasFilter):
	boxCarStart = Int(0, desc='The start index of the integration window in pts.')
	boxCarStop = Int(0, desc='The stop index of the integration window in pts.')
	IFfreq = Float(10e6, desc='The I.F. frequency for digital demodulation.')
	samplingRate = Float(250e6, desc='The sampling rate of the digitizer.')

class Correlator(MeasFilter):
	filters = List(MeasFilter)

if __name__ == "__main__":


	testFilter1 = DigitalHomodyne(name='M1', boxCarStart=100, boxCarStop=500, IFfreq=10e6, samplingRate=250e6)
	testFilter2 = DigitalHomodyne(name='M2', boxCarStart=150, boxCarStop=600, IFfreq=39.2e6, samplingRate=250e6)

	import enaml
	from enaml.stdlib.sessions import show_simple_view
	with enaml.imports():
		from MeasFiltersViews import MeasFilterManagerWindow
	session = show_simple_view(MeasFilterManagerWindow(filters=[testFilter1, testFilter2]))
