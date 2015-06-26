import h5py
import unittest
import os
import inspect

import json

import config
import Libraries
from test_Sequences import APS2Helper
import numpy as np

from atom.api import Atom, atomlist

class TestJSON(unittest.TestCase, APS2Helper):

	def setUp(self):
		APS2Helper.__init__(self)
		APS2Helper.setUp(self)

	def validate_json_dictionary(self, testDict, validDict):

		# top level
		for key in validDict.keys():
			print key
			assertIn(key, testDict)
			if isinstance(testDict[key], dict):
				print testDict[key]

	def validate_atomlist(self, test, truth):
		for i in range(len(truth)):
			if isinstance(truth[i], Atom):
				self.validate_atom(test[i], truth[i])
			elif isinstance(truth[i], atomlist):
				self.validate_atomlist(test[i], truth[i])
			else:
				self.assertEqual(test[i], truth[i])

	def validate_atom(self, test, truth):
		self.assertIsInstance(test, truth.__class__)
		testState = test.__getstate__()
		truthState = truth.__getstate__()
		for state in truthState:
			if isinstance(truthState[state], Atom):
				self.validate_atom(testState[state], truthState[state])
			elif isinstance(truthState[state], atomlist):
				self.validate_atomlist(testState[state], truthState[state])
			elif isinstance(truthState[state], np.ndarray):
				np.testing.assert_allclose(testState[state], truthState[state], rtol=1e-5, atol=0)
			else:
				self.assertEqual(testState[state], truthState[state])

	def validate_library(self, test, truth):
		for element in truth:
			self.assertIn(element, test)
			self.assertIsInstance(test[element], truth[element].__class__)
			if isinstance(truth[element], Atom):
				self.validate_atom(test[element], truth[element])
			else:
				print "Did not test: ", element


	def test_channels_library(self):
		Libraries.channelLib.channelDict = self.channels
		Libraries.channelLib.write_to_file()
		Libraries.channelLib.channelDict = {}
		Libraries.channelLib.load_from_library()

		self.validate_library(Libraries.channelLib.channelDict, self.channels)

	def test_instruments_library(self):
		Libraries.instrumentLib.instrDict = self.instruments
		Libraries.instrumentLib.write_to_file()
		Libraries.instrumentLib.instrDict = {}
		Libraries.instrumentLib.load_from_library()

		# can not test instrumentLib directly here must test enclosed dictionary
		self.validate_library(Libraries.instrumentLib.instrDict, self.instruments)

if __name__ == "__main__":
    unittest.main()
