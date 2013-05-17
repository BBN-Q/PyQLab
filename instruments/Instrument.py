from traits.api import HasTraits, Bool, Str

import json

class Instrument(HasTraits):
	"""
	Main super-class for all instruments.
	"""
	name = Str
	enabled = Bool(True, desc='Whether the unit is used/enabled.')
	address = Str('', desc='Address of instrument')

	def set_settings(self, settings):
		for key,value in settings.items():
			setattr(self, key, value)

	def json_encode(self, matlabCompatible=False):
		jsonDict = self.__getstate__()
		if matlabCompatible:
			jsonDict['deviceName'] = self.__class__.__name__
			jsonDict.pop('enabled', None)
			jsonDict.pop('name', None)
		else:
			jsonDict['x__class__'] = self.__class__.__name__
			jsonDict['x__module__'] = self.__class__.__module__
		return jsonDict

	def update_from_jsondict(self, jsonDict):
		for name,value in jsonDict.items():
			setattr(self, name, value)