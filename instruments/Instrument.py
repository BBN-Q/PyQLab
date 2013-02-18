from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'
from traits.api import HasTraits

import json

class Instrument(HasTraits):
	"""
	Main super-class for all instruments.
	"""

	def get_settings(self):
		return self.__getstate__()

	def set_settings(self, settings):
		for key,value in settings.items():
			setattr(self, key, value)
