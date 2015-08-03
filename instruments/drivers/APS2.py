from instruments.AWGBase import AWG, AWGDriver
from atom.api import Int, Constant

from APS2Pattern import *

class APS2(AWG):
	numChannels = Int(default=2)
	seqFileExt = Constant('.h5')

	empty_channel_set = {'ch12':{}, 'ch12m1':{}, 'ch12m2':{}, 'ch12m3':{}, 'ch12m4':{}}
	naming_convention = ['12', '12m1', '12m2', '12m3', '12m4']

	def read_sequence_file(self, filename):
		return read_APS2_file(filename)

	def write_sequence_file(self, data, filename):
		write_APS2_file(data, filename)
