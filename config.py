#Package startup stuff so people can start their iPython session with
#
#run PyQLab /path/to/cfgFile and be up and running


#Package imports
import numpy as np

#Load the configuration from the json file and populate the global configuration dictionary
import json
from os import getenv
PyQLabCfgFile = getenv('PYQLAB_CFGFILE')
if PyQLabCfgFile:
	with open(PyQLabCfgFile, 'r') as f:
		PyQLabCfg = json.load(f)

	#pull out the variables 
	AWGDir = PyQLabCfg['AWGDir']
	channelParamsFile = PyQLabCfg['ChannelParamsFile']
	instrumentLibFile = PyQLabCfg['InstrumentLibraryFile']
	sweepLibFile = PyQLabCfg['SweepLibraryFile']
	measurementLibFile = PyQLabCfg['MeasurementLibraryFile']

else:
	raise NameError("Unable to find the PyQLab configuration environment variable")




