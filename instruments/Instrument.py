from atom.api import Atom, Unicode, Bool

import json

class Instrument(Atom):
	"""
	Main super-class for all instruments.
	"""
	label = Unicode()
	enabled = Bool(True).tag(desc='Whether the unit is used/enabled.')
	address = Unicode('').tag(desc='Address of unit as GPIB address, IPv4 or USB string.')

	def json_encode(self, matlabCompatible=False):
		jsonDict = self.__getstate__()
		if matlabCompatible:
			jsonDict['deviceName'] = self.__class__.__name__
			jsonDict.pop('enabled', None)
			jsonDict.pop('label', None)
		else:
			jsonDict['x__class__'] = self.__class__.__name__
			jsonDict['x__module__'] = self.__class__.__module__
		return jsonDict

	def update_from_jsondict(self, jsonDict):
		jsonDict.pop('x__class__', None)
		jsonDict.pop('x__module__', None)
		for label,value in jsonDict.items():
			setattr(self, label, value)