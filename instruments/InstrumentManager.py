# import os
# os.environ['ETS_TOOLKIT'] = 'qt4'
# from traits.etsconfig.api import ETSConfig
# ETSConfig.toolkit = 'qt4'
from traits.api import HasTraits, List, Instance
from traitsui.api import TreeEditor, TreeNode, View, Item, VGroup, HGroup, spring



import sys
from pyface.qt import QtGui, QtCore

from MicrowaveSources import AgilentN51853A, MicrowaveSource, MicrowaveSourceView
from AWGs import AWG, APS

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

InstrumentEditor = TreeEditor(
	nodes=[
		TreeNode(node_for = [InstrumentLibrary],
				auto_open = True,
				children = '',
				label = '=Instrument Library',
				view = View()),
		TreeNode(node_for = [InstrumentLibrary],
				auto_open = True,
				children = 'sources',
				label = '=Sources',
				view = View()),
		TreeNode(node_for = [InstrumentLibrary],
				auto_open = True,
				children = 'AWGs',
				label = "=AWG's",
				view = View()),
		TreeNode(node_for = [InstrumentLibrary],
				auto_open = True,
				children = 'digitizers',
				label = "=Digitizers",
				view = View()),
		TreeNode(node_for = [MicrowaveSource],
				auto_open = True,
				label = 'name',
				view = MicrowaveSourceView),
		TreeNode(node_for = [AWG],
				auto_open = True,
				label = 'name')])


InstrumentLibraryView = View(Item(name='instrLib', editor=InstrumentEditor, show_label=False), title='InstrumentEditor', resizable=True)

class InstrumentManager(HasTraits):
	instrLib = Instance(InstrumentLibrary)

	def load_settings(self, settings):
		self.instrLib.load_settings(settings)


if __name__ == '__main__':
	#Look to see if iPython's event loop is running
	# app = QtCore.QCoreApplication.instance()
	# if app is None:
	# 	app = QtGui.QApplication(sys.argv)

	instruments = {}
	instruments['Agilent1'] = AgilentN51853A(name='Agilent1')
	instruments['Agilent2'] = AgilentN51853A(name='Agilent2')
	instruments['BBNAPS1'] = APS(name='BBNAPS1')

	instrMan = InstrumentManager()
	instrMan.instrLib = InstrumentLibrary()
	instrMan.load_settings(instruments)
	instrMan.configure_traits(view = InstrumentLibraryView)


	# mainWindow = InstrumentManager(instruments)
	# mainWindow.show()
	# sys.exit(app.exec_())

	# try: 
	#     from IPython.lib.guisupport import start_event_loop_qt4
	#     start_event_loop_qt4(app)
	# except ImportError:






	
	