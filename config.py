#Package startup stuff so people can start their iPython session with
#
#run PyQLab /path/to/cfgFile and be up and running


#Package imports
import numpy as np

#Load the configuration from the json file and populate the global configuration dictionary
import json
import os.path
import sys
PyQLabCfgFile = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
if PyQLabCfgFile:
	with open(PyQLabCfgFile, 'r') as f:
		PyQLabCfg = json.load(f)

	#pull out the variables 
	AWGDir = PyQLabCfg['AWGDir']
	channelLibFile = PyQLabCfg['ChannelLibraryFile']
	instrumentLibFile = PyQLabCfg['InstrumentLibraryFile']
	sweepLibFile = PyQLabCfg['SweepLibraryFile']
	measurementLibFile = PyQLabCfg['MeasurementLibraryFile']
	quickpickFile = PyQLabCfg['QuickPickFile'] if 'QuickPickFile' in PyQLabCfg else None

else:
	raise NameError("Unable to find the PyQLab configuration environment variable")

