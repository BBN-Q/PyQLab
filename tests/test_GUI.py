import unittest
import os
import json
import config
import time

import enaml
from enaml.qt.qt_application import QtApplication

from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

import ExpSettingsGUI

class TestExpSettingsGUI(unittest.TestCase):

	timeDelay = 5000

	@classmethod
	def setUpClass(cls):
		cls.removeFiles()

	def setUp(self):
		TestExpSettingsGUI.removeFiles()

	@classmethod
	def tearDownClass(cls):
		cls.removeFiles()

	@classmethod
	def removeFiles(cls):
		files = [config.channelLibFile,
				 config.instrumentLibFile,
				 config.sweepLibFile,
				 config.measurementLibFile,
				 config.quickpickFile]
		for file in files:
			if os.path.exists(file):
			 	os.remove(file)

	def left_click(self, enamlObject):
		qtObject = enamlObject.proxy.widget
		QTest.mouseClick(qtObject, Qt.LeftButton)

	def set_text(self, enamlObject, value):
		qtObject = enamlObject.proxy.widget
		qtObject.clear()
		QTest.keyClicks(qtObject, value)
		QTest.keyClick(qtObject, Qt.Key_Return)

	def set_keys(self, enamlObject, key):
		qtObject = enamlObject.proxy.widget
		QTest.keyClick(qtObject, key)


	def get_main_menu(self):
		return self.view.children[0]

	def get_main_notebook(self):
		return self.get_nested_child(self.view, (1, 0))

	def click_apply_button(self):
		button = self.get_nested_child(self.view, (1, 3))
		self.left_click(button)

	def get_page(self, title, pages = None):
		if pages is None:
			pages = self.get_main_notebook().children
		for page in pages:
			if page.title == title:
				return page
		return None

	def get_nested_child(self, baseObject, ids):
		object = baseObject
		for id in ids:
			#print object, object.children
			object = object.children[id]
		return object

	def get_notebook_page(self, notebook, page):
		notebook = self.get_page(notebook)
		pages = notebook.children[0].children[0].children
		page = self.get_page(page, pages)
		addButton = page.children[0].children[1]
		return page, addButton

	def populate_selector(self, page, name, num_down_arrows):
		dialog = self.get_nested_child(page,(0,1,0))
		field = self.get_nested_child(dialog,(0,1,1))
		model = self.get_nested_child(dialog,(0,1,3))
		addButton = self.get_nested_child(dialog,(0,2,0,0))
		self.set_text(field, name)
		for i in range(num_down_arrows):
			self.set_keys(model, Qt.Key_Down)
		self.left_click(addButton)

	def select_item(self, enamlObject, item):
		qtObject = enamlObject.proxy.widget
		qtObject.setCurrentRow(item)

	def set_physical_channel(self, item, awg):
		page, addButton = self.get_notebook_page('Channels', 'Logical')
		listWidget = self.get_nested_child(page, (0,0))
		self.select_item(listWidget,item)
		comboBox = self.get_nested_child(page, (0,3,0,0,1))
		for i in range(awg):
			self.set_keys(comboBox, Qt.Key_Down)

	def set_awg(self, item, awg, child):
		page, addButton = self.get_notebook_page('Channels', 'Physical')
		listWidget = self.get_nested_child(page, (0,0))
		self.select_item(listWidget,item)
		comboBox = self.get_nested_child(page, (0,3,0,0,child))
		for i in range(awg):
			self.set_keys(comboBox, Qt.Key_Down)

	def add_item(self, nb, pg, name, model):
		page, addButton = self.get_notebook_page(nb, pg)
		self.app.timed_call(self.timeDelay, self.populate_selector, page, name, model)
		self.left_click(addButton)

	def add_instrument(self, name, model):
		self.add_item('Instruments', "AWG's", name, model)

	def add_physical_channel(self, name, model):
		self.add_item('Channels', "Physical", name, model)

	def add_logical_channel(self, name, model):
		self.add_item('Channels', "Logical", name, model)

	def test_measurement_setup(self):
		TestExpSettingsGUI.removeFiles()
		import Libraries

		from ExpSettingsGUI import ExpSettings
		expSettings= ExpSettings(sweeps=Libraries.sweepLib, instruments=Libraries.instrumentLib,
								 measurements=Libraries.measLib,  channels=Libraries.channelLib)

		# setup on change AWG
		expSettings.instruments.AWGs.onChangeDelegate = expSettings.channels.on_awg_change

		with enaml.imports():
			from ExpSettingsView import ExpSettingsView

		self.app = QtApplication()
		self.view = ExpSettingsView(expSettings=expSettings)
		self.view.show()

		def run_test():
			self.add_instrument("APS1", 1)

			self.add_physical_channel("APS1-12", 1)
			self.set_awg(0, 1,1)

			self.add_physical_channel("APS1-12m1", 0)
			self.set_awg(1, 1,7)

			self.add_physical_channel("APS1-12m2", 0)
			self.set_awg(2, 1,7)

			self.add_physical_channel("APS1-12m3", 0)
			self.set_awg(3, 1,7)

			self.add_physical_channel("APS1-12m4", 0)
			self.set_awg(4, 1,7)

			self.add_logical_channel("digitizerTrig", 1)
			self.set_physical_channel(0, 1)

			self.add_logical_channel("slaveTrig", 1)
			self.set_physical_channel(1, 2)

			self.click_apply_button()
			self.app.stop()

			time.sleep(self.timeDelay/1000)
			Libraries.instrumentLib.load_from_library()
			Libraries.channelLib.load_from_library()

			testChannels = ["digitizerTrig",
							"slaveTrig",
							"APS1-12",
							"APS1-12m1",
							"APS1-12m2",
							"APS1-12m3",
							"APS1-12m4"]

			for channel in testChannels:
				self.assertIn(channel, Libraries.channelLib.channelDict)

			self.assertIn("APS1", Libraries.instrumentLib.instrDict)

		self.app.timed_call(self.timeDelay, run_test)
		self.app.start()


if __name__ == "__main__":
    unittest.main()
