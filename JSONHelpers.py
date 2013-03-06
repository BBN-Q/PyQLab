import json

from traits.api import HasTraits

from instruments.InstrumentManager import InstrumentLibrary
class QLabEncoder(json.JSONEncoder):
	"""
	Helper for QLab to encode all the classes we use.
	"""
	def default(self, obj):
		if isinstance(obj, HasTraits):
			#For the instrument library pull out enabled instruments from the dictionary
			if isinstance(obj, InstrumentLibrary):
				return {name:instr for name,instr in obj.instrDict.items() if instr.enabled}
			return obj.get()
		else:
			return super(QLabEncoder, self).default(obj)

