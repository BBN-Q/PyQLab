from traits.api import HasTraits, List, Instance, Float, Dict, Str, Property, on_trait_change
import enaml
from enaml.stdlib.sessions import show_simple_view

from Instrument import Instrument
from MicrowaveSources import MicrowaveSourceList, MicrowaveSource
from AWGs import AWGList, AWG

class InstrumentLibrary(HasTraits):
	#All the instruments are stored as a dictionary keyed of the instrument name
	instrDict = Dict(Str, Instrument)
	libFile = Str('InstrumentLibrary.json', transient=True)

	def write_to_file(self):
		#Move import here to avoid circular import
		import JSONHelpers
		with open(self.libFile,'w') as FID:
			json.dump(self, FID, cls=JSONHelpers.QLabEncoder, indent=2, sort_keys=True)

	def load_from_file(self):
		pass


if __name__ == '__main__':

	from MicrowaveSources import AgilentN51853A
	from AWGs import APS
	from InstrumentManager import InstrumentLibrary
	instruments = {}
	instruments['Agilent1'] = AgilentN51853A(name='Agilent1')
	instruments['Agilent2'] = AgilentN51853A(name='Agilent2')
	instruments['BBNAPS1'] = APS(name='BBNAPS1')
	instruments['BBNAPS2'] = APS(name='BBNAPS2')

	instrLib = InstrumentLibrary(instrDict=instruments)
	with enaml.imports():
		from InstrumentManagerView import InstrumentManagerWindow

	show_simple_view(InstrumentManagerWindow(instrLib=instrLib))








	
	