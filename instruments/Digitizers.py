"""
For now just Alazar cards but should also support Acquiris.
"""
from Instrument import Instrument

from atom.api import Atom, Str, Int, Float, Bool, Enum, List, Dict, Coerced
import itertools, ast

import enaml
from enaml.qt.qt_application import QtApplication

class Digitizer(Instrument):
	pass

class AlazarATS9870(Instrument):
	address = Str('1').tag(desc='Location of the card') #For now we only have one
	acquireMode = Enum('digitizer', 'averager').tag(desc='Whether the card averages on-board or returns single-shot data')
	clockType = Enum('ref')
	delay = Float(0.0).tag(desc='Delay from trigger')
	samplingRate = Float(100000000).tag(desc='Sampling rate in Hz')
	verticalScale = Float(1.0).tag(desc='Peak voltage (V)')
	verticalOffset = Float(0.0).tag(desc='Vertical offset (V)')
	verticalCoupling = Enum('AC','DC').tag(desc='AC/DC coupling')
	bandwidth = Enum('20MHz', 'Full').tag(desc='Input bandwidth filter')
	triggerLevel = Float(0.0).tag(desc='Trigger level (mV)')
	triggerSource = Enum('A','B','Ext').tag(desc='Trigger source')
	triggerCoupling = Enum('AC','DC').tag(desc='Trigger coupling')
	triggerSlope = Enum('rising','falling').tag(desc='Trigger slope')
	recordLength = Int(1024).tag(desc='Number of samples in each record')
	nbrSegments = Int(1).tag(desc='Number of segments in memory')
	nbrWaveforms = Int(1).tag(desc='Number of times each segment is repeated')
	nbrRoundRobins = Int(1).tag(desc='Number of times entire memory is looped')

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

class X6VirtualChannel(Atom):
	label = Str()
	enableDemodStream = Bool(True).tag(desc='Enable demodulated data stream')
	enableDemodResultStream = Bool(True).tag(desc='Enable demod result data stream')
	enableRawResultStream = Bool(True).tag(desc='Enable raw result data stream')
	IFfreq = Float(10e6).tag(desc='IF Frequency')
	demodKernel = Str().tag(desc='Integration kernel vector for demod stream')
	rawKernel = Str().tag(desc='Integration kernel vector for raw stream')
	threshold = Float(0.0).tag(desc='Qubit state decision threshold')

	def json_encode(self, matlabCompatible=False):
		jsonDict = self.__getstate__()
		if matlabCompatible:
			import numpy as np
			import base64
			try:
				jsonDict['demodKernel'] = base64.b64encode(eval(self.demodKernel))
			except:
				jsonDict['demodKernel'] = []
			try:
				jsonDict['rawKernel'] = base64.b64encode(eval(self.rawKernel))
			except:
				jsonDict['rawKernel'] = []
		return jsonDict

class X6(Instrument):
	recordLength = Int(1024).tag(desc='Number of samples in each record')
	nbrSegments = Int(1).tag(desc='Number of segments in memory')
	nbrWaveforms = Int(1).tag(desc='Number of times each segment is repeated')
	nbrRoundRobins = Int(1).tag(desc='Number of times entire memory is looped')
	enableRawStreams = Bool(False).tag(desc='Enable capture of raw data from ADCs')
	# channels = Dict(None, X6VirtualChannel)
	channels = Coerced(dict)
	digitizerMode = Enum('digitizer', 'averager').tag(desc='Whether the card averages on-board or returns single-shot data')

	def __init__(self, **traits):
		super(X6, self).__init__(**traits)
		if not self.channels:
			for a, b in itertools.product(range(1,3), range(1,3)):
				label = str((a,b))
				key = "s{0}{1}".format(a, b)
				self.channels[key] = X6VirtualChannel(label=label)

	def json_encode(self, matlabCompatible=False):
		jsonDict = super(X6, self).json_encode(matlabCompatible)
		if matlabCompatible:
			# For the Matlab experiment manager we nest averager settings
			map(lambda x: jsonDict.pop(x), ['recordLength', 'nbrSegments', 'nbrWaveforms', 'nbrRoundRobins'])
			jsonDict['averager'] = {k:getattr(self,k) for k in ['recordLength', 'nbrSegments', 'nbrWaveforms', 'nbrRoundRobins']}

		return jsonDict

	def update_from_jsondict(self, params):

		for chName, chParams in params['channels'].items():
			# if this is still a raw dictionary convert to object
			if isinstance(chParams, dict):
				chParams.pop('x__class__', None)
				chParams.pop('x__module__', None)
				chParams = X6VirtualChannel(**chParams)

			for paramName in chParams.__getstate__().keys():
				setattr(self.channels[chName], paramName, getattr(chParams, paramName))

		params.pop('channels')
		super(X6, self).update_from_jsondict(params)

if __name__ == "__main__":
	from Digitizers import X6
	digitizer = X6(label='scope')
	with enaml.imports():
		from DigitizersViews import TestX6Window

		app = QtApplication()
	view = TestX6Window(instr=digitizer)
	view.show()
	app.start()
