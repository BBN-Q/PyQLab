from atom.api import (Atom, List, ContainerList, Dict, observe, Callable, Typed)

class DictManager(Atom):
	"""
	Control - Presenter for a dictionary of items. 
	i.e. give the ability to add/delete rename items
	"""
	itemDict = Typed(dict)
	displayFilter = Callable() # filter which items to display later
	possibleItems = List() # a list of classes that can possibly be added to this list
	displayList = ContainerList() 

	def add_item(parent):
		"""
		Open a dialog box and add an instrument
		"""
		pass
		#Call a blocking dialog
		# dialog = AddDialog()
		# AddDialog(root_object(), dictManager=dictManager, newClassList=newClassList, objText=modelName)
		#...
		#Deal with the result
		# if ok 

	def remove_item(parent):
		pass

	def name_change():
		pass

	@observe('itemDict')
	def update_display_list(self, change):
		"""
		Eventualy itemDict will be a ContainerDict and this will fire on all events
		"""
		self.displayList = [v.label for v in self.itemDict.values() if self.displayFilter(v)]
