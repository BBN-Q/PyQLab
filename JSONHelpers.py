import json

from traits.api import HasTraits

from instruments.Instrument import Instrument
class QLabEncoder(json.JSONEncoder):
	"""
	Helper for QLab to encode all the classes we use.
	"""
	def default(self, obj):
		if isinstance(obj, HasTraits):
			return obj.get()
		else:
			return super(QLabEncoder, self).default(obj)

