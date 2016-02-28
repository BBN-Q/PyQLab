from instruments.AWGBase import AWG, AWGDriver
from atom.api import Int, Constant

class Tek5014(AWG, AWGDriver):
	numChannels = Int(default=4)
	seqFileExt = Constant('.awg')
	translator = Constant('TekPattern')

	naming_convention = ['12', '34', '1m1', '1m2', '2m1', '2m2', '3m1', '3m2', '4m1', '4m2']
