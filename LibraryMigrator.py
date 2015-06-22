
import config
import json

# Migrates json file versions using a version number
# File version prior to adding a version number are 0
# Version 1 adds the version to all json files
# Version 2+ change the structure of the files

# to add migrations add version_{n}_to_{n+1} methods
# to make the changes in the json dict 

class JSONMigrator(object):
	""" Base class for the JSON Migration

		Includes the base method for migrating
		Assumes migration methods are of the form version_{n}_to_{n+1}

		Includes version_0_to_1
	"""

	def __init__(self):
		self.fileName = None
		self.jsonDict = None
		self.min_version = 0
		self.max_version = 1

	def version(self):
		try:
			return self.jsonDict['version']
		except:
			return 0

	def load(self):
		try:
			with open(self.fileName, 'r') as FID:
			    self.jsonDict = json.load(FID)
		except IOError:
			print('json file {0} not found'.format(self.fileName))

	def is_class(self, dict, searchClasses):

		if type(searchClasses) == type(''):
			searchClasses = [searchClasses]

		if type(dict) != type({}):
			return False

		if 'x__class__' not in dict.keys():
			return False

		for className in searchClasses:
			if dict['x__class__'] == className:
				return True

		return False
	
	def save(self):
		with open(self.fileName,'w') as FID:
			json.dump(self.jsonDict, FID, indent=2, sort_keys=True)

	def migrate(self):
		self.load()
		while self.version() < self.max_version:
			migrate_function = "version_{0}_to_{1}".format(self.version(), self.version() + 1)
			print "Migrating: {0}.{1}()".format(self.__class__.__name__, migrate_function)
			function = getattr(self,migrate_function) 
			function()
			self.jsonDict['version'] = self.version() + 1
		self.save()

	def version_0_to_1(self):
		# does nothing but bump version number
		pass

class IntrumentMigrator(JSONMigrator):
	""" Migrator for the Intrument Manager JSON File """
	def __init__(self):
		super(IntrumentMigrator, self).__init__()
		self.fileName = config.instrumentLibFile

class ChannelMigrator(JSONMigrator):		
	""" Migrator for the Channel Manager JSON File """
	def __init__(self):
		super(ChannelMigrator, self).__init__()
		self.fileName = config.channelLibFile
		self.max_version = 2

	def version_1_to_2(self):

		if not self.is_class(self.jsonDict,'ChannelLibrary') or 'channelDict' not in self.jsonDict:
			print "Error json file is not a ChannelLibrary"
			return

		# Migration Setup 1
		# Move SSBFreq from Physical Chanel for Qubits to the Logical Qubit Channel

		lcClasses = ['Qubit']
		logicalChannels = [lc for lc in self.jsonDict['channelDict'] if 
							self.is_class(self.jsonDict['channelDict'][lc],lcClasses)]

		for lc in logicalChannels:
			pc = self.jsonDict['channelDict'][lc]['physChan']
			if pc not in self.jsonDict['channelDict']:
				print 'Error: Physical Channel {0} not found.'.format(pc)
				continue
			if 'SSBFreq' not in self.jsonDict['channelDict'][pc]:
				continue
			frequency = self.jsonDict['channelDict'][pc]['SSBFreq']
			del self.jsonDict['channelDict'][pc]['SSBFreq']
			self.jsonDict['channelDict'][lc]['SSBFreq'] = frequency

class SweepMigrator(JSONMigrator):		
	""" Migrator for the Sweeps JSON File """

	def __init__(self):
		super(SweepMigrator, self).__init__()
		self.fileName = config.sweepLibFile

class MeasurementMigrator(JSONMigrator):		
	""" Migrator for the Sweeps JSON File """

	def __init__(self):
		super(MeasurementMigrator, self).__init__()
		self.fileName = config.measurementLibFile

def migrate_all():
	migrators = [IntrumentMigrator, 
	             ChannelMigrator,
	             SweepMigrator,
	             MeasurementMigrator]
	
	for migrator in migrators:
		m = migrator()
		m.migrate()

if __name__ == '__main__':
	migrate_all()

