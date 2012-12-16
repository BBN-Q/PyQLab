#Package startup stuff so people can start their iPython session with
#
#run PyQLab /path/to/cfgFile and be up and running


#Package imports
from QGL import *
import numpy as np

#Load the configuration from the json file and populate the global configuration dictionary
import json
from os import getenv
PyQLabCfgFile = getenv('PyQLabCfgFile')
if PyQLabCfgFile:
	with open(PyQLabCfgFile, 'r') as f:
		PyQLabCfg = json.load(f)

	#pull out the variables 
	AWGDir = PyQLabCfg['AWGDir']
	ChannelParams = PyQLabCfg['ChannelParamsFile']

else:
	raise NameError("Unable to find the PyQLab configuration environment variable")




