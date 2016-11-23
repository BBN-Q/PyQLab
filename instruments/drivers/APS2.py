from instruments.AWGBase import AWG
from atom.api import Int, Constant, Enum

class APS2(AWG):
	num_channels = Int(default=2)
	seq_file_ext = Constant('.h5')
	translator = Constant('APS2Pattern')
	trigger_source = Enum('Internal', 'External', 'System').tag(desc='Source of trigger')

	naming_convention = ['12', '12m1', '12m2', '12m3', '12m4']

class APS2TDM(AWG):
	num_channels = Int(default=0)
	seq_file_ext = Constant('.h5')

	def json_encode(self):
		jsonDict = super(AWG, self).json_encode()

		# Delete unused properties
		unused = ["num_channels", "seq_file_ext", "trigger_source", "samplingRate", "seqFile", "seqForce", "delay", "channels"]
		for param in unused:
			del jsonDict[param]

		# pretend to be a normal APS2 for MATLAB
		if matlabCompatible:
			jsonDict['deviceName'] = 'APS2'

		return jsonDict

	def update_from_jsondict(self, params):
		for p in ['label', 'enabled', 'address', 'isMaster', 'triggerInterval']:
			setattr(self, p, params[p])
