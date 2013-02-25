
from traits.api import HasTraits, List, Instance
import enaml
from enaml.stdlib.sessions import show_simple_view
from enaml.qt.qt_application import QtApplication


from MicrowaveSources import MicrowaveSourceList, MicrowaveSource
from AWGs import AWGList, AWG

class InstrumentLibrary(HasTraits):
	#The instrument library basically has lists of Sources, AWGs and Digitizers
	sources = List(MicrowaveSource)
	AWGs = List(AWG)
	digitizers = List()

	def load_settings(self, settings):
		#Loop over the instruments and add to appropriate list
		for instr in settings.values():
			if isinstance(instr, MicrowaveSource):
				self.sources.append(instr)
			elif isinstance(instr, AWG):
				self.AWGs.append(instr)

if __name__ == '__main__':

	from MicrowaveSources import AgilentN51853A
	from AWGs import APS
	instruments = {}
	instruments['Agilent1'] = AgilentN51853A(name='Agilent1')
	instruments['Agilent2'] = AgilentN51853A(name='Agilent2')
	instruments['BBNAPS1'] = APS(name='BBNAPS1')

	instrLib = InstrumentLibrary()
	instrLib.load_settings(instruments)
	with enaml.imports():
		from InstrumentManagerView import InstrumentManagerView

	show_simple_view(InstrumentManagerView(instrLib=instrLib))

	# app = QtApplication([session])
	# app.start_session('Test')
	# app.start()







	
	