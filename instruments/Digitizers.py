"""
For now just Alazar cards but should also support Acquiris.
"""
from Instrument import Instrument

from traits.api import Str, Int, Float, Bool, Enum

import enaml
from enaml.stdlib.sessions import show_simple_view

class AlazarATS9870(Instrument):
	address = Str('1', desc='Location of the card') #For now we only have one
	acquireMode = Enum('digitizer', 'averager', desc='Whether the card averages on-board or returns single-shot data')
	clockType = Enum('ref')
	delay = Float(0.0, desc='Delay from trigger')
	samplingRate = Float(100000000, desc='Sampling rate in Hz')
	verticalScale = Float(1.0, desc='Peak voltage (V)')
	verticalOffset = Float(0.0, desc='Vertical offset (V)')
	verticalCoupling = Enum('AC','DC', desc='AC/DC coupling')
	bandwidth = Enum('20MHz', 'Full', desc='Input bandwidth filter')
	triggerLevel = Float(0.0, desc='Trigger level (mV)')
	triggerSource = Enum('A','B','Ext', desc='Trigger source')
	triggerCoupling = Enum('AC','DC', desc='Trigger coupling')
	triggerSlope = Enum('rising','falling', desc='Trigger slope')
	recordLength = Int(1024, desc='Number of samples in each record')
	nbrSegments = Int(1, desc='Number of segments in memory')
	nbrWaveforms = Int(1, desc='Number of times each segment is repeated')
	nbrRoundRobins = Int(1, desc='Number of times entire memory is looped')

	def json_encode(self, matlabCompatible=False):
		if matlabCompatible:
			"For the Matlab experiment manager we seperately nest averager, horizontal, vertical settings"
			jsonDict = {}
			jsonDict['address'] = self.address
			jsonDict['deviceName'] = 'AlazarATS9870'
			jsonDict['horizontal'] = {'delayTime':self.delay, 'samplingRate':self.samplingRate}
			jsonDict['vertical'] = {k:getattr(self,k) for k in ['verticalScale', 'verticalOffset', 'verticalCoupling', 'bandwidth']}
			jsonDict['trigger'] = {k:getattr(self,k) for k in ['triggerLevel', 'triggerSource', 'triggerCoupling', 'triggerSlope']}
			jsonDict['averager'] = {k:getattr(self,k) for k in ['recordLength', 'nbrSegments', 'nbrWaveforms', 'nbrRoundRobins']}
			#Add the other necessities
			jsonDict['acquireMode'] = self.acquireMode
			jsonDict['clockType'] = self.clockType
		else:
			jsonDict = super(AlazarATS9870, self).json_encode(matlabCompatible)

		return jsonDict

if __name__ == "__main__":
	from Digitizers import AlazarATS9870
	digitizer = AlazarATS9870(name='scope')
	with enaml.imports():
		from DigitizersViews import TestAlazarWindow

	session = show_simple_view(TestAlazarWindow(instr=digitizer))
	
