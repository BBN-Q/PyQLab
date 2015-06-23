
import config
import json

# Migrates json file versions using a version number
# File version prior to adding a version number are 0
# Version 1 adds the version to all json files
# Version 2+ change the structure of the files

# to add migrations add version_{n}_to_{n+1} methods in the subclasses of JSONMigrator
# currently  [IntrumentMigrator, ChannelMigrator,SweepMigrator, MeasurementMigrator]
# to make the changes in the json dict 

class JSONMigrator(object):
	""" Base class for the JSON Migration

		Includes the base method for migrating
		Assumes migration methods are of the form version_{n}_to_{n+1}

		Includes version_0_to_1
	"""

	def __init__(self, fileName, libraryClass, primaryKey, max_version = 1):
		self.fileName = fileName
		self.jsonDict = None
		self.min_version = 0
		self.max_version = max_version
		self.primaryKey = primaryKey
		self.primaryDict = None
		self.libraryClass = libraryClass

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
			self.jsonDict = None
		
		if not self.json_input_validate():
			self.jsonDict = None
			return

		# cache primary dictionary
		self.primaryDict = self.jsonDict[self.primaryKey]

	def json_input_validate(self):
		if not self.is_class(self.jsonDict, self.libraryClass) or self.primaryKey  not in self.jsonDict:
			print "Error json file is not a " + self.libraryClass
			return False
		return True

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
		# store primary dictionary back into json dictionary
		self.jsonDict[self.primaryKey] = self.primaryDict

		# write out file
		with open(self.fileName,'w') as FID:
			json.dump(self.jsonDict, FID, indent=2, sort_keys=True)

	def migrate(self):
		self.load()
		if self.jsonDict:
			while self.version() < self.max_version:
				migrate_function = "version_{0}_to_{1}".format(self.version(), self.version() + 1)
				print "Migrating: {0}.{1}()".format(self.__class__.__name__, migrate_function)
				function = getattr(self,migrate_function) 
				function()
				self.jsonDict['version'] = self.version() + 1
			self.save()

	def get_items_matching_class(self, classes):
		return [a for a in self.primaryDict if self.is_class(self.primaryDict[a],classes)]

	def version_0_to_1(self):
		# does nothing but bump version number
		pass

class IntrumentMigrator(JSONMigrator):
	""" Migrator for the Intrument Manager JSON File """
	def __init__(self):
		super(IntrumentMigrator, self).__init__(
			config.instrumentLibFile, 
			"InstrumentLibrary",
			"instrDict",
			2)

	def version_1_to_2(self):

		# Migration step 1
		# Change Labbrick64 class to Labbrick

		chClasses = ['Labbrick64']
		lb64 = self.get_items_matching_class(chClasses)

		for lb in lb64:
			self.primaryDict[lb]['x__class__'] = "Labbrick"
							

class ChannelMigrator(JSONMigrator):		
	""" Migrator for the Channel Manager JSON File """
	def __init__(self):
		super(ChannelMigrator, self).__init__(
			config.channelLibFile, 
			'ChannelLibrary',
			'channelDict',
			2)

	def version_1_to_2(self):

		# Migration step 1
		# Move SSBFreq from Physical Chanel for Qubits to the Logical Qubit Channel

		lcClasses = ['Qubit', 'Measurement']
		logicalChannels = self.get_items_matching_class(lcClasses)

		for lc in logicalChannels:
			pc = self.primaryDict[lc]['physChan']
			if pc not in self.primaryDict:
				print 'Error: Physical Channel {0} not found.'.format(pc)
				continue
			if 'SSBFreq' not in self.primaryDict[pc]:
				continue
			frequency = self.primaryDict[pc]['SSBFreq']
			del self.primaryDict[pc]['SSBFreq']
			self.primaryDict[lc]['frequency'] = frequency

class SweepMigrator(JSONMigrator):		
	""" Migrator for the Sweeps JSON File """

	def __init__(self):
		super(SweepMigrator, self).__init__(
			config.sweepLibFile,
			"SweepLibrary",
			"sweepDict",
			1)
		

class MeasurementMigrator(JSONMigrator):		
	""" Migrator for the Sweeps JSON File """

	def __init__(self):
		super(MeasurementMigrator, self).__init__(
			config.measurementLibFile,
			"MeasFilterLibrary",
			"filterDict",
			1)

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

