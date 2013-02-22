
from traits.api import HasTraits, List, Instance
from traitsui.api import TreeEditor, TreeNode, View, Item, VGroup, HGroup, spring, Handler
from traitsui.menu import Menu, Action, Separator
from traitsui.qt4.tree_editor import NewAction, DeleteAction, RenameAction

from MicrowaveSources import MicrowaveSourceList, MicrowaveSource, MicrowaveSourceView

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

print_sources = Action(name='Print sources..', action='handler.print_sources(object)')
print_awgs = Action(name='Print AWGs...', action='handler.print_awgs(object)')

class TreeHandler(Handler):

	def print_sources(self, object):
		for instr in object.sources:
			print(instr.name)

	def print_awgs(self, object):
		for instr in object.AWGs:
			print(instr.name)

InstrumentEditor = TreeEditor(
	nodes=[
		TreeNode(node_for = [InstrumentLibrary],
				auto_open = True,
				children = '',
				label = '=Instrument Library',
				view = View(width=600, height=200)), #empty view with some sizing for the instrument panels
		TreeNode(node_for = [InstrumentLibrary],
				auto_open = True,
				children = 'sources',
				label = '=Sources',
				view = View(),
				menu = Menu(NewAction, print_sources),
				add = MicrowaveSourceList),
		TreeNode(node_for = [InstrumentLibrary],
				auto_open = True,
				children = 'AWGs',
				label = "=AWG's",
				view = View(),
				menu = Menu(NewAction, print_awgs),
				add = AWGList),
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
		TreeNode(node_for = AWGList,
				auto_open = True,
				menu = Menu(DeleteAction, Separator(), RenameAction),
				label = 'name')])

InstrumentLibraryView = View(Item(name='instrLib', editor=InstrumentEditor, show_label=False),
					 title='InstrumentEditor', handler=TreeHandler(), resizable=True)

class InstrumentManager(HasTraits):
	instrLib = Instance(InstrumentLibrary, ())

	def load_settings(self, settings):
		self.instrLib.load_settings(settings)


if __name__ == '__main__':

	from MicrowaveSources import AgilentN51853A
	from AWGs import APS
	instruments = {}
	instruments['Agilent1'] = AgilentN51853A(name='Agilent1')
	instruments['Agilent2'] = AgilentN51853A(name='Agilent2')
	instruments['BBNAPS1'] = APS(name='BBNAPS1')

	instrMan = InstrumentManager()
	instrMan.load_settings(instruments)
	instrMan.configure_traits(view = InstrumentLibraryView)







	
	