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
