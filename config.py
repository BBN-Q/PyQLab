#Package configuration information

import json
import os.path
import sys

#Load the configuration from the json file and populate the global configuration dictionary
rootFolder = os.path.dirname( os.path.abspath(__file__) )
rootFolder = rootFolder.replace('\\', '/') # use unix-like convention
PyQLabCfgFile = os.path.join(rootFolder, 'config.json')
if not os.path.isfile(PyQLabCfgFile):
	# build a config file from the template
	templateFile = os.path.join(rootFolder, 'config.example.json')
	ifid = open(templateFile, 'r')
	ofid = open(PyQLabCfgFile, 'w')
	for line in ifid:
		ofid.write(line.replace('/my/path/to', rootFolder))
	ifid.close()
	ofid.close()


with open(PyQLabCfgFile, 'r') as f:
	PyQLabCfg = json.load(f)

#pull out the variables
#abspath allows the use of relative file names in the config file
AWGDir = os.path.abspath(PyQLabCfg['AWGDir'])
instrumentLibFile = os.path.abspath(PyQLabCfg['InstrumentLibraryFile'])
sweepLibFile = os.path.abspath(PyQLabCfg['SweepLibraryFile'])
measurementLibFile = os.path.abspath(PyQLabCfg['MeasurementLibraryFile'])
quickpickFile = os.path.abspath(PyQLabCfg['QuickPickFile']) if 'QuickPickFile' in PyQLabCfg else ''
