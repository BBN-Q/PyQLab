import os
os.environ['ETS_TOOLKIT'] = 'qt4'

import sys
from pyface.qt import QtGui, QtCore

from MicrowaveSources import AgilentN51853A, MicrowaveSource, MicrowaveSourceView
from AWGs import AWG

class InstrumentManager(QtGui.QWidget):
	"""
	A widget for managing instruments and instrument settings.
	"""
	def __init__(self, instruments, parent=None):
		super(InstrumentManager, self).__init__(parent=parent)

		self.instruments = instruments


		hSplitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)


		instrumentTree = QtGui.QTreeWidget()
		instrumentTree.setHeaderLabel('Instrument Library')

		sources = QtGui.QTreeWidgetItem(['Sources'])
		awgs = QtGui.QTreeWidgetItem(['AWGs'])
		self.instrViews = {}

		for instrName, instr in self.instruments.items():
			if isinstance(instr, MicrowaveSource):
				sources.addChild(QtGui.QTreeWidgetItem([instrName]))
				self.instrViews[instrName] = instr.edit_traits(view=MicrowaveSourceView).control
			if isinstance(instr, AWG):
				awgs.addChild(QtGui.QTreeWidgetItem([instrName]))
				self.instrViews[instrName] = instr.edit_traits().control
			self.instrViews[instrName].hide()

		instrumentTree.addTopLevelItem(sources)
		instrumentTree.addTopLevelItem(awgs)
		instrumentTree.itemClicked.connect(lambda item: self.update_view(item))



		#Add the buttons for adding/deleting channels
		tmpWidget = QtGui.QWidget()

		vBox = QtGui.QVBoxLayout(tmpWidget)
		vBox.addWidget(instrumentTree)


		hBox = QtGui.QHBoxLayout()
		addChanButton = QtGui.QPushButton('Add')
		# addChanButton.clicked.connect(self.add_channel)
		hBox.addWidget(addChanButton)
		deleteChanButton = QtGui.QPushButton('Delete')
		# deleteChanButton.clicked.connect(self.delete_channel)
		hBox.addWidget(deleteChanButton)
		hBox.addStretch(1)
		vBox.addLayout(hBox)   

		hSplitter.addWidget(tmpWidget)
		for view in self.instrViews.values():
			hSplitter.addWidget(view)

		self.setWindowTitle('Instrument Manager')
		self.resize(600, 480)


	def update_view(self, showItem):
		for itemName, widget in self.instrViews.items():
			if itemName == showItem.text(0):
				widget.show()
			else:
				widget.hide()



if __name__ == '__main__':
	#Look to see if iPython's event loop is running
	app = QtCore.QCoreApplication.instance()
	if app is None:
		app = QtGui.QApplication(sys.argv)

	instruments = {}
	instruments['Agilent1'] = AgilentN51853A()
	instruments['Agilent2'] = AgilentN51853A()
	mainWindow = InstrumentManager(instruments)
	mainWindow.show()
	sys.exit(app.exec_())

	# try: 
	#     from IPython.lib.guisupport import start_event_loop_qt4
	#     start_event_loop_qt4(app)
	# except ImportError:






	
	