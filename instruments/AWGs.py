"""
AWGs
"""

from traits.api import HasTraits, List, Instance, Str, Int, Float, Range, Bool, Enum, File

from Instrument import Instrument

import enaml
from enaml.stdlib.sessions import show_simple_view


class AWGChannel(Instrument):
	amplitude = Range(value=1.0, low=0.0, high=1.0, desc="Scaling applied to channel amplitude")
	offset = Range(value=0.0, low=-1.0, high=1.0, desc='D.C. offset applied to channel')
	enabled = Bool(True, desc='Whether the channel output is enabled.')

class AWG(Instrument):
	triggerSource = Enum('Internal', 'External', desc='Source of trigger')
	triggerInterval = Float(1e-4, desc='Internal trigger interval')
	samplingRate = Float(1200, desc='Sampling rate in MHz')
	numChannels = Int
	channels = List(AWGChannel)
	seqFile = File(desc='Path to sequence file.')

	def __init__(self, **traits):
		super(AWG, self).__init__(**traits)
		for ct in range(self.numChannels):
			self.channels.append(AWGChannel(name='Chan. {}'.format(ct+1)))

	def get_stack_view(self):
		with enaml.imports():
			from AWGViews import AWGStackView
		return AWGStackView(myAWG=self)


class APS(AWG):
	numChannels = 4

class Tek5014(AWG):
	numChannels = 4
	pass

AWGList = [APS, Tek5014]

if __name__ == "__main__":

	with enaml.imports():
		from AWGViews import AWGView
	
	awg = APS(name='BBNAPS1')
	session = show_simple_view(AWGView(awg=awg))
