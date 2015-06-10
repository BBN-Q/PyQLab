import h5py
import unittest
import numpy as np
import time
import os.path

import Libraries
from QGL import *
import QGL

from QGL.Channels import Measurement, LogicalMarkerChannel, PhysicalMarkerChannel, PhysicalQuadratureChannel, ChannelLibrary
from instruments.AWGs import APS2, APS, Tek5014
from instruments.InstrumentManager import InstrumentLibrary

import time

import ExpSettingsVal

class ChannelMap(object):

	def __init__(self):
		self.channels = {}
		self.instruments = {}
		self.assign_channels()


	def finalize_map(self, mapping):
		for name,value in mapping.iteritems():
			self.channels[name].physChan = self.channels[value]

		Compiler.channelLib = ChannelLibrary()
		Compiler.channelLib.channelDict = self.channels

		Compiler.instrumentLib = InstrumentLibrary()
		Compiler.instrumentLib.instrDict = self.instruments

		(self.q1, self.q2) = self.get_qubits()
	
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

		for name in self.logical_names:
			self.channels[name] = LogicalMarkerChannel(label=name)

	def get_qubits(self):
		return [QGL.Compiler.channelLib[name] for name in self.qubit_names]

class TestSequences(object):

	def test_AllXY(self):
		AllXY(self.q1)

	# def test_CR_PiRabi(self):
	#  	PiRabi(self.q1, self.q2)

	# def test_CR_EchoCRLen(self):
	#  	EchoCRLen(self.q1, self.q2)

	# def test_CR_EchoCRPhase(self):
	#  	EchoCRPhase(self.q1, self.q2)


	# def test_Decoupling_HannEcho(self):
	#  	HahnEcho(self.q1)

	# def test_Decoupling_CPMG(self):		
	#  	CPMG(self.q1)

	# def test_FlipFlop(self):
	#  	FlipFlop(self.q1)

	# def test_T1T2_InversionRecovery(self):
	#  	InversionRecovery(self.q1)

	def test_T1T2_Ramsey(self):
	 	Ramsey(self.q1, np.linspace(0, 5e-6, 11))

	# def test_SPAM(self):
	#  	SPAM(self.q1)	


class TestAPS2(unittest.TestCase, ChannelMap, TestSequences):

	def setUp(self):
		ChannelMap.__init__(self)
		for name in ['APS1', 'APS2', 'APS3', 'APS4']:
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
					'M-q2-gate':'APS4-12m1'}
		
		self.finalize_map(mapping)
			

class TestAPS1(unittest.TestCase, ChannelMap, TestSequences):

	def setUp(self):
		ChannelMap.__init__(self)
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
					'q2-gate'      :'APS1-4m1'}
		self.finalize_map(mapping)

class TestTek5014(unittest.TestCase, ChannelMap, TestSequences):

	def setUp(self):
		ChannelMap.__init__(self)
		for name in ['TEK1']:
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
					'q2-gate'		:'TEK1-4m1'}
		self.finalize_map(mapping)

if __name__ == "__main__":    
    unittest.main()