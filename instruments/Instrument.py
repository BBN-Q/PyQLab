from traits.api import HasTraits, Bool

import json

class Instrument(HasTraits):
	"""
	Main super-class for all instruments.
	"""
	enabled = Bool(True, desc='Whether the unit is used/enabled.')

	def get_settings(self):
		return self.__getstate__()

	def set_settings(self, settings):
		for key,value in settings.items():
			setattr(self, key, value)
