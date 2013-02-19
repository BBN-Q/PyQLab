# import os
# os.environ['ETS_TOOLKIT'] = 'qt4'
# from traits.etsconfig.api import ETSConfig
# ETSConfig.toolkit = 'qt4'
from traits.api import HasTraits, List, Instance
from traitsui.api import TreeEditor, TreeNode, View, Item, VGroup, HGroup, spring, Handler
from traitsui.menu import Menu, Action, Separator
from traitsui.qt4.tree_editor import NewAction, DeleteAction, RenameAction


import sys
from pyface.qt import QtGui, QtCore

from MicrowaveSources import MicrowaveSourceList, MicrowaveSource, MicrowaveSourceView

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

PrintSources = Action(name='Print sources..', action='handler.print_sources(object)')

class TreeHandler(Handler):

	def print_sources(self, object):
		print('Got here!')
		print(object.__dict__)
		for instr in object.sources:
			print(instr.name)

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
				view = View(),
				menu = Menu(NewAction, PrintSources),
				add = MicrowaveSourceList),
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
		TreeNode(node_for = MicrowaveSourceList,
				auto_open = True,
				label = 'name',
				menu = Menu(DeleteAction, Separator(), RenameAction),
				view = MicrowaveSourceView),
		TreeNode(node_for = [AWG],
				auto_open = True,
				menu = Menu(DeleteAction, Separator(), RenameAction),
				label = 'name')])


InstrumentLibraryView = View(Item(name='instrLib', editor=InstrumentEditor, show_label=False),
					 title='InstrumentEditor', handler=TreeHandler(), width=.3, resizable=True)

class InstrumentManager(HasTraits):
	instrLib = Instance(InstrumentLibrary)

	def load_settings(self, settings):
		self.instrLib.load_settings(settings)


if __name__ == '__main__':
	#Look to see if iPython's event loop is running
	# app = QtCore.QCoreApplication.instance()
	# if app is None:
	# 	app = QtGui.QApplication(sys.argv)

	from MicrowaveSources import AgilentN51853A
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






	
	