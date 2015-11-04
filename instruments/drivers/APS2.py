from instruments.AWGBase import AWG, AWGDriver
from atom.api import Int, Constant, Enum

from APS2Pattern import *

class APS2(AWG):
	numChannels = Int(default=2)
	seqFileExt = Constant('.h5')
	triggerSource = Enum('Internal', 'External', 'System').tag(desc='Source of trigger')

	empty_channel_set = {'ch12':{}, 'ch12m1':{}, 'ch12m2':{}, 'ch12m3':{}, 'ch12m4':{}}
	naming_convention = ['12', '12m1', '12m2', '12m3', '12m4']

	def read_sequence_file(self, filename):
		return read_APS2_file(filename)

	def write_sequence_file(self, data, filename):
		write_APS2_file(data, filename)

class APS2TDM(AWG):
	numChannels = Int(default=0)
	seqFileExt = Constant('.h5')

	def json_encode(self, matlabCompatible=False):
		jsonDict = super(AWG, self).json_encode(matlabCompatible)

		# Delete unused properties
		unused = ["numChannels", "seqFileExt", "triggerSource", "samplingRate", "seqFile", "seqForce", "delay", "channels"]
		for param in unused:
			del jsonDict[param]

		# pretend to be a normal APS2 for MATLAB
		if matlabCompatible:
			jsonDict['deviceName'] = 'APS2'

		return jsonDict

	def update_from_jsondict(self, params):
		for p in ['label', 'enabled', 'address', 'isMaster', 'triggerInterval']:
			setattr(self, p, params[p])
