from instruments.AWGBase import AWG, AWGDriver
from atom.api import Int, Constant

from TekPattern import *

class Tek7000(AWG):
	numChannels = Int(default=2)
	seqFileExt = Constant('.awg')

	empty_channel_set = {'ch12':{}, 'ch1m1':{}, 'ch1m2':{}, 'ch2m1':{}, 'ch2m2':{}}

	def read_sequence_file(self,filename):
		return read_Tek_file(filename)

	def write_sequence_file(self,data, filename):
		write_Tek_file(data, filename,1)
