from instruments.AWGBase import AWG
from atom.api import Int, Constant

class Tek7000(AWG):
	numChannels = Int(default=2)
	seqFileExt = Constant('.awg')
	translator = Constant('TekPattern')
