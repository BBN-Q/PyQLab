from instruments.AWGBase import AWG
from atom.api import Int, Constant, Enum

class APS2(AWG):
	numChannels = Int(default=2)
	seqFileExt = Constant('.h5')
	translator = Constant('APS2Pattern')
	triggerSource = Enum('Internal', 'External', 'System').tag(desc='Source of trigger')

	naming_convention = ['12', '12m1', '12m2', '12m3', '12m4']

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
