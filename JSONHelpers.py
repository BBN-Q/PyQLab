import json, sys

from traits.api import HasTraits

import instruments
from Sweeps import Sweep, SweepLibrary
from MeasFilters import MeasFilterLibrary

from types import FunctionType

class LibraryEncoder(json.JSONEncoder):
	"""
	Helper for QLab to encode all the classes we use.
	"""
	def default(self, obj):
		#For the pulse functions in channels just return the name
		if isinstance(obj, FunctionType):
			return obj.__name__
		elif isinstance(obj, HasTraits):
			jsonDict = obj.__getstate__()

			#For channels' linked AWG or generator just return the name
			from QGL.Channels import PhysicalChannel
			if isinstance(obj, PhysicalChannel):
				awg = jsonDict.pop('AWG')
				jsonDict['AWG'] = awg.name
				source = jsonDict.pop('generator')
				jsonDict['generator'] = source.name

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

	def dict_to_obj(self, jsonDict):
		if '__class__' in jsonDict:
			#Pop the class and module
			className = jsonDict.pop('__class__')
			moduleName = jsonDict.pop('__module__')
			__import__(moduleName)

			#Re-encode the strings as ascii (this should go away in Python 3)
			args = {k.encode('ascii'):v for k,v in jsonDict.items()}

			#For points sweeps pop the stop
			if moduleName == 'Sweeps':
				jsonDict.pop('stop', None)

			inst = getattr(sys.modules[moduleName], className)(**args)

			return inst
		else:
			return jsonDict

class ChannelDecoder(json.JSONDecoder):

	def __init__(self, instrLib=None, **kwargs):
		super(ChannelDecoder, self).__init__(object_hook=self.dict_to_obj, **kwargs)
		self.instrLib = instrLib

	def dict_to_obj(self, jsonDict):
		if '__class__' in jsonDict:
			#Pop the class and module
			className = jsonDict.pop('__class__')
			moduleName = jsonDict.pop('__module__')
			__import__(moduleName)

			#Re-encode the strings as ascii (this should go away in Python 3)
			args = {k.encode('ascii'):v for k,v in jsonDict.items()}

			#Instantiate the instruments associated with channels
			awg = args.pop('AWG', None)
			if awg:
				args['AWG'] = self.instrLib[awg]
			generator = args.pop('generator', None)
			if generator:
				args[generator] = self.instrLib[generator]

			inst = getattr(sys.modules[moduleName], className)(**args)

			return inst
		else:
			return jsonDict


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
			#For the sweep library we return a list of sweeps in order
			elif isinstance(obj, SweepLibrary):
				return [obj.sweepDict[k] for k in obj.sweepOrder]
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
			#Inject the sweep type for sweeps
			elif isinstance(obj, Sweep):
				jsonDict = obj.__getstate__()
				jsonDict['type'] = obj.__class__.__name__
			else:
				jsonDict = obj.__getstate__()

			#Strip out __traits_version__
			jsonDict.pop('__traits_version__', None)

			return jsonDict

		else:
			return super(QLabEncoder, self).default(obj)	
	
