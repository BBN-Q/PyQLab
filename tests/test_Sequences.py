import h5py
import unittest
import numpy as np
import time
import os

import config
import Libraries
from QGL import *
import QGL

from QGL.Channels import Measurement, LogicalChannel, LogicalMarkerChannel, PhysicalMarkerChannel, PhysicalQuadratureChannel, ChannelLibrary
from instruments.AWGs import APS2, APS, Tek5014
from instruments.InstrumentManager import InstrumentLibrary

import ExpSettingsVal

BASE_AWG_DIR = config.AWGDir

class AWGTestHelper(object):
	testFileDirectory = './tests/test_data/awg/'

	def __init__(self, read_function = None):
		self.channels = {}
		self.instruments = {}
		self.assign_channels()
		self.set_awg_dir()
		self.read_function = read_function

	def finalize_map(self, mapping):
		for name,value in mapping.iteritems():
			self.channels[name].physChan = self.channels[value]

		Compiler.channelLib = ChannelLibrary()
		Compiler.channelLib.channelDict = self.channels

		Compiler.instrumentLib = InstrumentLibrary()
		Compiler.instrumentLib.instrDict = self.instruments

		(self.q1, self.q2) = self.get_qubits()
		self.cr = self.channels["cr"]
	
	def assign_channels(self):

		self.qubit_names = ['q1','q2']
		self.logical_names = ['digitizerTrig', 'slaveTrig']

		self.assign_logical_channels()
	
	def assign_logical_channels(self):

		for name in self.qubit_names:
			mName = 'M-' + name
			mgName = 'M-' + name + '-gate'
			qgName = name + '-gate'

			mg = LogicalMarkerChannel(label=mgName)
			qg = LogicalMarkerChannel(label=qgName)

			m = Measurement(label=mName, gateChan = mg)
			
			q = Qubit(label=name, gateChan=qg)
			q.pulseParams['length'] = 30e-9

			self.channels[name] = q
			self.channels[mName] = m
			self.channels[mgName]  = mg
			self.channels[qgName]  = qg	
			
			self.channels['cr-gate']  = LogicalMarkerChannel(label='cr-gate')
			cr = Qubit(label="cr", gateChan = self.channels['cr-gate'] )	
			cr.pulseParams['length'] = 30e-9
			self.channels["cr"] = cr
			

		for name in self.logical_names:
			self.channels[name] = LogicalMarkerChannel(label=name)

	def get_qubits(self):
		return [QGL.Compiler.channelLib[name] for name in self.qubit_names]

	def set_awg_dir(self, footer = ""):
		cn = self.__class__.__name__

		self.awg_dir = os.path.abspath(BASE_AWG_DIR + os.path.sep + cn)
		self.truth_dir = os.path.abspath(self.testFileDirectory + os.path.sep + cn)

		if footer != "":
			self.awg_dir = self.awg_dir + os.path.sep + footer
			self.truth_dir = self.truth_dir + os.path.sep + footer

		if not os.path.isdir(self.awg_dir):
			os.mkdir(self.awg_dir)
		config.AWGDir = self.awg_dir 

	def compare_sequences(self, seqDir):
		if not self.read_function:
			print "AWGTestHelper.read_function is not defined"
			return

		searchDirectory = self.awg_dir + os.path.sep + seqDir
		truthDirectory = self.truth_dir + os.path.sep + seqDir

		filenames = os.listdir(searchDirectory)
		for filename in filenames:
			truthFile = truthDirectory + os.path.sep + filename
			testFile = searchDirectory + os.path.sep + filename

			self.assertTrue(os.path.isfile(truthFile), "Truth Data File: {0} not found.".format(truthFile) )
			self.compare_file_data(testFile, truthFile)

	def compare_file_data(self, testFile, truthFile):
		awgData = self.read_function(testFile)
		truthData = self.read_function(truthFile)

		awgDataLen = len(awgData)
		truthDataLen = len(truthData)

		self.assertTrue(awgDataLen == truthDataLen, 
			"Expected {0} sequences in file. Found {1}.".format(truthDataLen, awgDataLen))

		for name in truthData:
			self.assertTrue(name in awgData, "Expected sequence {0} not found in file {1}".format(name, testFile))
			
			if len(truthData[name][0]) == 1:
				seqA = np.array(truthData[name])
				seqB = np.array(awgData[name])
				self.compare_sequence(seqA,seqB, "\nFile {0} =>\n\tSequence {1}".format(testFile, name))
			else:
				for x in range(1,len(truthData[name])):
					seqA = np.array(truthData[name][x])
					seqB = np.array(awgData[name][x])
					self.compare_sequence(seqA,seqB,  "\nFile {0} =>\n\tSequence {1} Element{2}".format(testFile, name, x))

	def compare_sequence(self, seqA, seqB, errorHeader):
		self.assertTrue( seqA.size == seqB.size, "{0} size {1} != size {2}".format(errorHeader, str(seqA.size), str(seqB.size)))
		np.testing.assert_allclose(seqA, seqB, rtol=1e-5, atol=0)


class TestSequences(object):

	def compare_sequences(self): abstract

	def test_AllXY(self):
		self.set_awg_dir()
		AllXY(self.q1)
		self.compare_sequences('AllXY')

	def test_CR_PiRabi(self):
		self.set_awg_dir()
	  	PiRabi(self.q1, self.q2, self.cr,  np.linspace(0, 5e-6, 11))
	  	self.compare_sequences('PiRabi')

	def test_CR_EchoCRLen(self):
		self.set_awg_dir('EchoCRLen')
	  	EchoCRLen(self.q1, self.q2, self.cr,  np.linspace(0, 5e-6, 11))
	  	self.compare_sequences('EchoCR')

	def test_CR_EchoCRPhase(self):
		self.set_awg_dir('EchoCRPhase')
	  	EchoCRPhase(self.q1, self.q2, self.cr,  np.linspace(0, pi/2, 11))
	  	self.compare_sequences('EchoCR')

	def test_Decoupling_HannEcho(self):
		self.set_awg_dir()
	 	HahnEcho(self.q1, np.linspace(0, 5e-6, 11))
	 	self.compare_sequences('Echo')

	def test_Decoupling_CPMG(self):
		self.set_awg_dir()
	 	CPMG(self.q1, np.linspace(0, 2, 4), np.linspace(0, 5e-6, 11))
	 	self.compare_sequences('CPMG')

	def test_FlipFlop(self):
		self.set_awg_dir()
	  	FlipFlop(self.q1, np.linspace(0, 5e-6, 11))
	  	self.compare_sequences('FlipFlop')

	def test_T1T2_InversionRecovery(self):
		self.set_awg_dir()
	  	InversionRecovery(self.q1,  np.linspace(0, 5e-6, 11))
	  	self.compare_sequences('T1')

	def test_T1T2_Ramsey(self):
		self.set_awg_dir()
	 	Ramsey(self.q1, np.linspace(0, 5e-6, 11))
	 	self.compare_sequences('Ramsey')

	def test_SPAM(self):
		self.set_awg_dir()
	  	SPAM(self.q1, np.linspace(0, pi/2, 11))	
	  	self.compare_sequences('SPAM')

	def test_Rabi_RabiAmp(self):
		self.set_awg_dir('RabiAmp')
		RabiAmp(self.q1,  np.linspace(0, 5e-6, 11))
		self.compare_sequences('Rabi')

	def test_Rabi_RabiWidth(self):
		self.set_awg_dir('RabiWidth')
		RabiWidth(self.q1,  np.linspace(0, 5e-6, 11))
		self.compare_sequences('Rabi')	

	def test_Rabi_RabiAmp_TwoQubits(self):
		self.set_awg_dir('RabiAmp2')
		RabiAmp_TwoQubits(self.q1, self.q2, np.linspace(0, 5e-6, 11),  np.linspace(0, 5e-6, 11))
		self.compare_sequences('Rabi')	

	def test_Rabi_RabiAmpPi(self):
		self.set_awg_dir('RabiAmpPi')
		RabiAmpPi(self.q1, self.q2, np.linspace(0, 5e-6, 11))
		self.compare_sequences('Rabi')	

	def test_Rabi_SingleShot(self):
		self.set_awg_dir()
		SingleShot(self.q1)
		self.compare_sequences('SingleShot')	

	def test_Rabi_PulsedSpec(self):
		self.set_awg_dir()
		PulsedSpec(self.q1)
		self.compare_sequences('Spec')

	# def test_RB_SingleQubitRB(self):
	# 	self.set_awg_dir('SingleQubitRB')
	# 	PulsedSpec(self.q1, create_RB_seqs(1, range(1,10)))
	# 	self.compare_sequences('RB')

	# def test_RB_TwoQubitRB(self):
	# 	self.set_awg_dir('TwoQubitRB')
	# 	PulsedSpec(self.q1, create_RB_seqs(2, range(1,10)))
	# 	self.compare_sequences('RB')
		

class TestAPS2(unittest.TestCase, AWGTestHelper, TestSequences):

	def setUp(self):
		AWGTestHelper.__init__(self, APS2Pattern.read_APS2_file)
		for name in ['APS1', 'APS2', 'APS3', 'APS4', 'APS5']:
			self.instruments[name] = APS2(label=name)

			channelName = name + '-12'
			channel = PhysicalQuadratureChannel(label=channelName)
			channel.AWG = self.instruments[name]
			self.channels[channelName] = channel

			for m in range(1,5):
				channelName = "{0}-12m{1}".format(name,m)
				channel = PhysicalMarkerChannel(label=channelName)
				channel.AWG = self.instruments[name]
				self.channels[channelName] = channel

		mapping = {	'digitizerTrig' : 'APS1-12m1',
				   	'slaveTrig': 'APS1-12m2',
			       	'q1':'APS1-12',
					'q1-gate':'APS1-12m3',
					'M-q1':'APS2-12',
					'M-q1-gate':'APS2-12m1',
					'q2':'APS3-12',
					'q2-gate':'APS3-12m1',
					'M-q2':'APS4-12',
					'M-q2-gate':'APS4-12m1',
					'cr' : 'APS5-12', 
					'cr-gate' : 'APS5-12m1'}
		
		self.finalize_map(mapping)
			

class TestAPS1(unittest.TestCase, AWGTestHelper, TestSequences):

	def setUp(self):
		AWGTestHelper.__init__(self, APSPattern.read_APS_file)
		for name in ['APS1', 'APS2']:
			self.instruments[name] = APS(label=name)

			for ch in ['12', '34']:
				channelName = name + '-' + ch
				channel = PhysicalQuadratureChannel(label=channelName)
				channel.AWG = self.instruments[name]
				self.channels[channelName] = channel

			for m in range(1,5):
				channelName = "{0}-{1}m1".format(name,m)
				channel = PhysicalMarkerChannel(label=channelName)
				channel.AWG = self.instruments[name]
				self.channels[channelName] = channel

		mapping = {	'digitizerTrig':'APS2-1m1',
					'slaveTrig'    :'APS2-2m1',
					'q1'           :'APS1-12',
					'M-q1'         :'APS1-12',
					'M-q1-gate'    :'APS1-1m1',
					'q1-gate'      :'APS1-2m1',
					'q2'           :'APS1-34',
					'M-q2'         :'APS1-34',
					'M-q2-gate'    :'APS1-3m1',
					'q2-gate'      :'APS1-4m1',
					'cr'           :'APS2-12', 
					'cr-gate'      :'APS2-1m1'}
		self.finalize_map(mapping)

class TestTek5014(unittest.TestCase, AWGTestHelper, TestSequences):

	def setUp(self):
		AWGTestHelper.__init__(self, TekPattern.read_Tek_file)
		for name in ['TEK1', 'TEK2']:
			self.instruments[name] = Tek5014(label=name)

			for ch in ['12', '34']:
				channelName = name + '-' + ch
				channel = PhysicalQuadratureChannel(label=channelName)
				channel.AWG = self.instruments[name]
				self.channels[channelName] = channel

			for m in ['1m1', '1m2', '2m1', '2m2', '3m1', '3m2', '4m1', '4m2']:
				channelName = "{0}-{1}".format(name,m)
				channel = PhysicalMarkerChannel(label=channelName)
				channel.AWG = self.instruments[name]
				self.channels[channelName] = channel

		mapping = { 'digitizerTrig'	:'TEK1-1m2',
					'slaveTrig'   	:'TEK1-2m2',
					'q1'			:'TEK1-12',
					'M-q1'			:'TEK1-12',
					'M-q1-gate'		:'TEK1-1m1',
					'q1-gate'		:'TEK1-2m1',
					'q2'			:'TEK1-34',
					'M-q2'			:'TEK1-34',
					'M-q2-gate'		:'TEK1-3m1',
					'q2-gate'		:'TEK1-4m1',
					'cr'            :'TEK2-12',
					'cr-gate'       :'TEK2-1m1'}
		self.finalize_map(mapping)

if __name__ == "__main__":    
    unittest.main()