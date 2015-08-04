from instruments.AWGBase import AWG, AWGDriver
from atom.api import Int, Constant

from TekPattern import *

class Tek5014(AWG, AWGDriver):
	numChannels = Int(default=4)
	seqFileExt = Constant('.awg')

	empty_channel_set = {'ch12':{}, 'ch34':{}, 'ch1m1':{}, 'ch1m2':{}, 'ch2m1':{}, 'ch2m2':{}, 'ch3m1':{}, 'ch3m2':{} , 'ch4m1':{}, 'ch4m2':{}}
	naming_convention = ['12', '34', '1m1', '1m2', '2m1', '2m2', '3m1', '3m2', '4m1', '4m2']

	def read_sequence_file(self,filename):
		return read_Tek_file(filename)

	def write_sequence_file(self,data, filename):
		write_Tek_file(data, filename,1)
