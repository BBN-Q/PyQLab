import json, sys

from traits.api import HasTraits

import instruments
import instruments.DCSources
from Sweeps import Sweep, SweepLibrary
from MeasFilters import MeasFilterLibrary

from QGL.Channels import PhysicalChannel, LogicalChannel, PhysicalQuadratureChannel
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
			if isinstance(obj, instruments.Instrument.Instrument):
				jsonDict = obj.json_encode(matlabCompatible=False)
			else:
				jsonDict = obj.__getstate__()
				#Inject the class name for decoding
				jsonDict['__class__'] = obj.__class__.__name__
				jsonDict['__module__'] = obj.__class__.__module__

			#For channels' linked AWG or generator just return the name
			if isinstance(obj, PhysicalChannel):
				awg = jsonDict.pop('AWG')
				if awg:
					jsonDict['AWG'] = awg.name
				source = jsonDict.pop('generator', None)
				if source:
					jsonDict['generator'] = source.name

			if isinstance(obj, LogicalChannel):
				physChan = jsonDict.pop('physChan')
				if physChan:
					jsonDict['physChan'] = physChan.name
			if isinstance(obj, PhysicalQuadratureChannel):
				gateChan = jsonDict.pop('gateChan')
				if gateChan:
					jsonDict['gateChan'] = gateChan.name

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
			jsonDict = {k.encode('ascii'):v for k,v in jsonDict.items()}

			inst = getattr(sys.modules[moduleName], className)()
			if hasattr(inst, 'update_from_jsondict'):
				inst.update_from_jsondict(jsonDict)
			else:
				inst = getattr(sys.modules[moduleName], className)(**jsonDict)

			return inst
		else:
			return jsonDict

class ChannelDecoder(json.JSONDecoder):

	def __init__(self, **kwargs):
		super(ChannelDecoder, self).__init__(object_hook=self.dict_to_obj, **kwargs)

	def dict_to_obj(self, jsonDict):
		import QGL.PulseShapes
		from Libraries import instrumentLib
		if '__class__' in jsonDict:
			#Pop the class and module
			className = jsonDict.pop('__class__')
			moduleName = jsonDict.pop('__module__')
			__import__(moduleName)

			#Re-encode the strings as ascii (this should go away in Python 3)
			jsonDict = {k.encode('ascii'):v for k,v in jsonDict.items()}

			#Instantiate the instruments associated with channels
			awg = jsonDict.pop('AWG', None)
			if awg:
				jsonDict['AWG'] = instrumentLib[awg]
			generator = jsonDict.pop('generator', None)
			if generator:
				jsonDict['generator'] = instrumentLib[generator]

			inst = getattr(sys.modules[moduleName], className)(**jsonDict)

			return inst
		else:
			#Re-encode the strings as ascii (this should go away in Python 3)
			jsonDict = {k.encode('ascii'):v for k,v in jsonDict.items()}
			shapeFun = jsonDict.pop('shapeFun',None)
			if shapeFun:
				jsonDict['shapeFun'] = getattr(QGL.PulseShapes, shapeFun)
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
				# reset all 'order' fields to -1, then re-label
				for sweep in obj.sweepDict.values():
					sweep.order = -1
				for ct, sweep in enumerate(obj.sweepOrder):
					obj.sweepDict[sweep].order = ct+1
				jsonDict = {name:sweep for name,sweep in obj.sweepDict.items() if name in obj.sweepOrder}
			#For instruments we need to add the Matlab deviceDriver name
			elif isinstance(obj, instruments.Instrument.Instrument):
				jsonDict = obj.json_encode(matlabCompatible=True)
				#If in CWMode, add the run method to AWGs
				if self.CWMode and isinstance(obj, instruments.AWGs.AWG):
					jsonDict['run'] = '{}'
			#Inject the sweep type for sweeps
			elif isinstance(obj, Sweep):
				jsonDict = obj.__getstate__()
				jsonDict['type'] = obj.__class__.__name__
				jsonDict.pop('enabled', None)
			else:
				jsonDict = obj.__getstate__()

			#Strip out __traits_version__
			jsonDict.pop('__traits_version__', None)
			jsonDict.pop('name', None)

			return jsonDict

		else:
			return super(ScripterEncoder, self).default(obj)	
	
