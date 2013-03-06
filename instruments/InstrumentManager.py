from traits.api import HasTraits, List, Instance, Float, Dict, Str, Property, on_trait_change
import enaml
from enaml.stdlib.sessions import show_simple_view

from Instrument import Instrument
from MicrowaveSources import MicrowaveSourceList, MicrowaveSource
from AWGs import AWGList, AWG

class InstrumentLibrary(HasTraits):
	#All the instruments are stored as a dictionary keyed of the instrument name
	instrDict = Dict(Str, Instrument)

	#For the view we keep separate lists by type
	#These could be cached properties but then I can't write back to them from the view
	sources = List(MicrowaveSource)
	AWGs = List(AWG)

	@on_trait_change('instrDict[]')
	def update_lists(self):
		self.sources = filter(lambda instr: isinstance(instr, MicrowaveSource), self.instrDict.values())
		self.AWGs = filter(lambda instr: isinstance(instr, AWG), self.instrDict.values())

	def add_instrument(self, newInstr):
		self.instrDict[newInstr.name] = newInstr

	def remove_instrument(self, deadInstrName):
		del self.instrDict[deadInstrName]


if __name__ == '__main__':

	from MicrowaveSources import AgilentN51853A
	from AWGs import APS
	instruments = {}
	instruments['Agilent1'] = AgilentN51853A(name='Agilent1')
	instruments['Agilent2'] = AgilentN51853A(name='Agilent2')
	instruments['BBNAPS1'] = APS(name='BBNAPS1')
	instruments['BBNAPS2'] = APS(name='BBNAPS2')

	instrLib = InstrumentLibrary(instrDict=instruments)
	with enaml.imports():
		from InstrumentManagerView import InstrumentManagerWindow

	show_simple_view(InstrumentManagerWindow(instrLib=instrLib))








	
	