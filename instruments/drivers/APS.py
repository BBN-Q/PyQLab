from instruments.AWGBase import AWG
from atom.api import Int, Constant

class APS(AWG):
	numChannels = Int(default=4)
	miniLLRepeat = Int(0).tag(desc='How many times to repeat each miniLL')
	seqFileExt = Constant('.h5')
	translator = Constant('APSPattern')

	naming_convention = ['12', '34', '1m1', '2m1', '3m1', '4m1']
