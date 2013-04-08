import json, sys

from traits.api import HasTraits

import instruments
from Sweeps import Sweep, SweepLibrary
from MeasFilters import MeasFilterLibrary

from collections import OrderedDict

class LibraryEncoder(json.JSONEncoder):
	"""
	Helper for QLab to encode all the classes we use.
	"""
	def default(self, obj):
		if isinstance(obj, HasTraits):
			jsonDict = obj.__getstate__()

			#Inject the class name for decoding
			jsonDict['__class__'] = obj.__class__.__name__
			jsonDict['__module__'] = obj.__class__.__module__

			#Strip out __traits_version__
			if '__traits_version__' in jsonDict:
				del jsonDict['__traits_version__']

			return jsonDict

		else:
			return super(LibraryEncoder, self).default(obj)

class LibraryDecoder(json.JSONDecoder):

	def __init__(self, **kwargs):
		super(LibraryDecoder, self).__init__(object_hook=self.dict_to_obj, **kwargs)

	def dict_to_obj(self, d):
		if '__class__' in d:
			#Pop the class and module
			className = d.pop('__class__')
			moduleName = d.pop('__module__')
			#Re-encode the strings as ascii (this should go away in Python 3)
			__import__(moduleName)
			args = {k.encode('ascii'):v for k,v in d.items()}
			inst = getattr(sys.modules[moduleName], className)(**args)

			return inst
		else:
			return d

class ScripterEncoder(json.JSONEncoder):
	"""
	Helper for QLab to encode all the classes for the matlab experiment script.
	"""
	def __init__(self, CWMode=False, **kwargs):
		super(ScripterEncoder, self).__init__(**kwargs)
		self.CWMode = CWMode

	def default(self, obj):
		if isinstance(obj, HasTraits):
			#For the instrument library pull out enabled instruments from the dictionary
			if isinstance(obj, instruments.InstrumentManager.InstrumentLibrary):
				jsonDict = {name:instr for name,instr in obj.instrDict.items() if instr.enabled}
			#For the measurment library just pull-out enabled measurements from the filter dictionary
			elif isinstance(obj, MeasFilterLibrary):
				jsonDict = {name:filt for name,filt in obj.filterDict.items() if filt.enabled}
			#For the scope we nest the averager, vertical, horizontal settings
			elif isinstance(obj, instruments.Digitizers.AlazarATS9870):
				jsonDict = obj.get_scripter_dict()
			#For instruments we need to add the Matlab deviceDriver name
			elif isinstance(obj, instruments.Instrument.Instrument):
				jsonDict = obj.__getstate__()
				jsonDict['deviceName'] = obj.__class__.__name__
				#If it is an AWG convert channel list into dictionary
				channels = jsonDict.pop('channels', None)
				if channels:
					for ct,chan in enumerate(channels):
						jsonDict['chan_{}'.format(ct+1)] = chan
				#If in CWMode, add the run method to AWGs
				if self.CWMode:
					if isinstance(obj, instruments.AWGs.AWG):
						jsonDict['run'] = '{}'
			else:
				jsonDict = obj.__getstate__()

			#Strip out __traits_version__
			if '__traits_version__' in jsonDict:
				del jsonDict['__traits_version__']

			return jsonDict

		else:
			return super(QLabEncoder, self).default(obj)	
	

class ChannelEncoder(json.JSONEncoder):
	'''
	Helper class to flatten the channel classes to a dictionary for json serialization.
	We just keep the class name and the properties
	'''
	def default(self, obj):
		#For the pulse function just return the name
		if isinstance(obj, FunctionType):
			return obj.__name__
		else:
			jsonDict = {'__class__': obj.__class__.__name__}
			#Strip leading underscores off private properties
			newDict = { key.lstrip('_'):value for key,value in obj.__dict__.items()}
			jsonDict.update(newDict)
			return jsonDict

class ChannelDecoder(json.JSONDecoder):
	'''
	Helper function to convert a json representation of a channel back into an object.
	'''
	def __init__(self, **kwargs):
		super(ChannelDecoder, self).__init__(object_hook=self.dict_to_obj, **kwargs)

	def dict_to_obj(self, jsonDict):
		#Extract the class name from the dictionary
		#If there is no class then assume top level dictionary
		if '__class__' not in jsonDict:
			return jsonDict
		else:
			className = jsonDict.pop('__class__')
			class_ = getattr(sys.modules[__name__], className)
			#Deal with shape functions
			if 'pulseParams' in jsonDict:
				if 'shapeFun' in jsonDict['pulseParams']:
					jsonDict['pulseParams']['shapeFun'] = getattr(PulseShapes, jsonDict['pulseParams']['shapeFun'])
			return class_(**jsonDict)
