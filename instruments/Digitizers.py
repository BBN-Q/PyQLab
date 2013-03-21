"""
For now just Alazar cards but should also support Acquiris.
"""
from Instrument import Instrument

from traits.api import Str, Int, Float, Bool, Enum

import enaml
from enaml.stdlib.sessions import show_simple_view

class AlazarATS9870(Instrument):
	acquireMode = Enum('digitizer', 'averager', desc='Whether the card averages on-board or returns single-shot data')
	delay = Float(0.0, desc='Delay from trigger')
	samplingRate = Int(100000000, desc='Sampling rate in Hz')
	verticalScale = Float(1.0, desc='Peak voltage (V)')
	verticalOffset = Float(0.0, desc='Vertical offset (V)')
	verticalCoupling = Enum('AC','DC', desc='AC/DC coupling')
	triggerLevel = Float(0.0, desc='Trigger level (mV)')
	triggerSource = Enum('A','B','Ext', desc='Trigger source')
	triggerCoupling = Enum('AC','DC', desc='Trigger coupling')
	triggerSlope = Enum('rising','falling', desc='Trigger slope')
	recordLength = Int(1024, desc='Number of samples in each record')
	nbrSegments = Int(1, desc='Number of segments in memory')
	nbrWaveforms = Int(1, desc='Number of times each segment is repeated')
	nbrRoundRobins = Int(1, desc='Number of times entire memory is looped')

if __name__ == "__main__":
	from Digitizers import AlazarATS9870
	digitizer = AlazarATS9870(name='scope')
	with enaml.imports():
		from DigitizersViews import TestAlazarWindow

	session = show_simple_view(TestAlazarWindow(myAlazar=digitizer))
	
