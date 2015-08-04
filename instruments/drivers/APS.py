from instruments.AWGBase import AWG, AWGDriver
from atom.api import Int, Constant

from APSPattern import *

class APS(AWG):
	numChannels = Int(default=4)
	miniLLRepeat = Int(0).tag(desc='How many times to repeat each miniLL')
	seqFileExt = Constant('.h5')

	empty_channel_set = {'ch12':{}, 'ch34':{}, 'ch1m1':{}, 'ch2m1':{}, 'ch3m1':{}, 'ch4m1':{}}
	naming_convention = ['12', '34', '1m1', '2m1', '3m1', '4m1']

	def read_sequence_file(self,filename):
		return read_APS_file(filename)

	def write_sequence_file(self,data, filename):
		write_APS_file(data, filename)
