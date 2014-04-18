import json, sys

from atom.api import Atom

import instruments
import instruments.DCSources
from Sweeps import Sweep, SweepLibrary
import MeasFilters
from QGL.Channels import PhysicalChannel, LogicalChannel, PhysicalQuadratureChannel
from types import FunctionType

class LibraryEncoder(json.JSONEncoder):
	"""
	Helper for QLab to encode all the classes we use.
	"""
	def default(self, obj):
		if isinstance(obj, Atom):
			#Check for a json_encode option
			try:
				jsonDict = obj.json_encode()
			except AttributeError:
				jsonDict = obj.__getstate__()
			except:
				print("Unexpected error encoding to JSON")
				raise 

			#Inject the class name for decoding
			jsonDict['x__class__'] = obj.__class__.__name__
			jsonDict['x__module__'] = obj.__class__.__module__

			return jsonDict

		else:
			return super(LibraryEncoder, self).default(obj)	

class LibraryDecoder(json.JSONDecoder):

	def __init__(self, **kwargs):
		super(LibraryDecoder, self).__init__(object_hook=self.dict_to_obj, **kwargs)

	def dict_to_obj(self, jsonDict):
		if 'x__class__' in jsonDict or '__class__' in jsonDict:
			#Pop the class and module
			className = jsonDict.pop('x__class__', None)
			if not className:
				className = jsonDict.pop('__class__')
			moduleName = jsonDict.pop('x__module__', None)
			if not moduleName:
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
		if 'x__class__' in jsonDict or '__class__' in jsonDict:
			#Pop the class and module
			className = jsonDict.pop('x__class__', None)
			if not className:
				className = jsonDict.pop('__class__')
			moduleName = jsonDict.pop('x__module__', None)
			if not moduleName:
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
		if isinstance(obj, Atom):
			#Check for a json_encode option
			try:
				jsonDict = obj.json_encode(matlabCompatible=True)
			except AttributeError:
				jsonDict = obj.__getstate__()
			except:
				print("Unexpected error encoding to JSON")
				raise 

			#Patch up some issues on the JSON dictionary

			#If in CWMode, add the run method to AWGs
			if self.CWMode and isinstance(obj, instruments.AWGs.AWG):
				jsonDict['run'] = '{}'

			#Matlab doesn't use the label
			jsonDict.pop('label', None)

			return jsonDict

		else:
			return super(ScripterEncoder, self).default(obj)	

