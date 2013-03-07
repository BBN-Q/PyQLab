import json

from traits.api import HasTraits

from instruments.InstrumentManager import InstrumentLibrary
from instruments.Instrument import Instrument
from Sweeps import Sweep

class QLabEncoder(json.JSONEncoder):
	"""
	Helper for QLab to encode all the classes we use.
	"""
	def default(self, obj):
		if isinstance(obj, HasTraits):
			#For the instrument library pull out enabled instruments from the dictionary
			if isinstance(obj, InstrumentLibrary):
				tmpDict = {name:instr for name,instr in obj.instrDict.items() if instr.enabled}
			#For sweeps we need to return instrument name and stop there
			elif isinstance(obj, Sweep):
				tmpDict = obj.__getstate__()
				if 'instr' in tmpDict:
					tmpDict['instr'] = tmpDict['instr'].name
			#For instruments we need to add the class name
			elif isinstance(obj, Instrument):
				tmpDict = obj.__getstate__()
				#If it is and AWG convert channel list into dictionary
				channels = tmpDict.pop('channels', None)
				if channels:
					for ct,chan in enumerate(channels):
						tmpDict['chan_{}'.format(ct+1)] = chan 
				tmpDict['deviceName'] = obj.__class__.__name__
			else:
				tmpDict = obj.__getstate__()

			#Strip out __traits_version__
			if '__traits_version__' in tmpDict:
				del tmpDict['__traits_version__']
			return tmpDict
		else:
			return super(QLabEncoder, self).default(obj)

