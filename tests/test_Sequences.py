import h5py
import unittest
import numpy as np
import time
import os.path

import Libraries
import QGL
from QGL import *


from QGL.Channels import Measurement, LogicalMarkerChannel, PhysicalMarkerChannel, PhysicalQuadratureChannel, ChannelLibrary
from instruments.AWGs import APS2, APS
from instruments.InstrumentManager import InstrumentLibrary

import time

import ExpSettingsVal



class ChannelMap(object):

	def assign_channels(self):

		self.ready = False
		self.qubit_names = ['q1','q2']
		self.logical_names = ['digitizerTrig', 'slaveTrig']

		self.reset()
		self.assign_logical_channels()
		self.assign_physical_channels()

		self.ready = ExpSettingsVal.validate_dynamic_lib(QGL.Compiler.channelLib, QGL.Compiler.instrumentLib)

		# write libraries out and reload
		QGL.Compiler.channelLib.write_to_file()
		QGL.Compiler.instrumentLib.write_to_file()

		reload(Libraries)
		reload(QGL)

		QGL.Compiler.channelLib = Libraries.channelLib
		QGL.Compiler.instrumentLib = Libraries.instrumentLib

		ExpSettingsVal.validate_lib()

	def print_physical_channels(self):
		print "Listing physical channel mapping:"
		for channel in QGL.Compiler.channelLib.keys():
			if isinstance(QGL.Compiler.channelLib[channel], QGL.Channels.LogicalChannel):
				print "\t", channel, " => " , repr(QGL.Compiler.channelLib[channel].physChan)

	def reset(self):

		QGL.Compiler.channelLib = ChannelLibrary()
		QGL.Compiler.instrumentLib = InstrumentLibrary()

	def assign_logical_channels(self):

		for name in self.qubit_names:
			q = Qubit(label=name)
			q.pulseParams['length'] = 30e-9

			QGL.Compiler.channelLib[name] = q

			mName = 'M-' + name
			QGL.Compiler.channelLib[mName]  = Measurement(label=mName)

			mName = 'M-' + name + '-gate'
			QGL.Compiler.channelLib[mName]  = LogicalMarkerChannel(label=mName)

			qName = name + '-gate'
			QGL.Compiler.channelLib[qName]  = LogicalMarkerChannel(label=qName)

		for name in self.logical_names:
			QGL.Compiler.channelLib[name] = LogicalMarkerChannel(label=name)

	def assign_physical_channels(self): abstract


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
		self.assign_channels()
		(self.q1, self.q2) = self.get_qubits()
		assert(self.ready == True)

	def assign_physical_channels(self):

		for name in ['APS1', 'APS2']:
			QGL.Compiler.instrumentLib.instrDict[name] = APS2()

			channelName = name + '-12'
			channel = PhysicalQuadratureChannel(label=channelName)
			channel.AWG.label = name
			QGL.Compiler.channelLib[channelName] = channel

			for m in range(1,5):
				channelName = "{0}-12m{1}".format(name,m)
				channel = PhysicalMarkerChannel(label=channelName)
				channel.AWG.label = name
				QGL.Compiler.channelLib[channelName] = channel

		QGL.Compiler.channelLib['digitizerTrig'].physChan = QGL.Compiler.channelLib['APS1-12m1']
		QGL.Compiler.channelLib['slaveTrig'].physChan = QGL.Compiler.channelLib['APS1-12m2']

		QGL.Compiler.channelLib['q1'].physChan = QGL.Compiler.channelLib['APS1-12']
		QGL.Compiler.channelLib['M-q1'].physChan = QGL.Compiler.channelLib['APS1-12']
		QGL.Compiler.channelLib['M-q1-gate'].physChan = QGL.Compiler.channelLib['APS1-12m3']
		QGL.Compiler.channelLib['q1-gate'].physChan = QGL.Compiler.channelLib['APS1-12m4']
		
		QGL.Compiler.channelLib['q2'].physChan = QGL.Compiler.channelLib['APS2-12']
		QGL.Compiler.channelLib['M-q2'].physChan = QGL.Compiler.channelLib['APS2-12']
		QGL.Compiler.channelLib['M-q2-gate'].physChan = QGL.Compiler.channelLib['APS2-12m1']
		QGL.Compiler.channelLib['q2-gate'].physChan = QGL.Compiler.channelLib['APS2-12m2']
			

class TestAPS1(unittest.TestCase, ChannelMap, TestSequences):

	def setUp(self):
		self.assign_channels()
		(self.q1, self.q2) = self.get_qubits()
		assert(self.ready == True)

	def assign_physical_channels(self):

		for name in ['APS1', 'APS2']:
			QGL.Compiler.instrumentLib.instrDict[name] = APS()

			for ch in ['12', '34']:
				channelName = name + '-' + ch
				channel = PhysicalQuadratureChannel(label=channelName)
				channel.AWG.label = name
				QGL.Compiler.channelLib[channelName] = channel

			for m in range(1,5):
				channelName = "{0}-{1}m1".format(name,m)
				channel = PhysicalMarkerChannel(label=channelName)
				channel.AWG.label = name
				QGL.Compiler.channelLib[channelName] = channel

		QGL.Compiler.channelLib['digitizerTrig'].physChan = QGL.Compiler.channelLib['APS2-1m1']
		QGL.Compiler.channelLib['slaveTrig'].physChan = QGL.Compiler.channelLib['APS2-2m1']

		QGL.Compiler.channelLib['q1'].physChan = QGL.Compiler.channelLib['APS1-12']
		QGL.Compiler.channelLib['M-q1'].physChan = QGL.Compiler.channelLib['APS1-12']
		QGL.Compiler.channelLib['M-q1-gate'].physChan = QGL.Compiler.channelLib['APS1-1m1']
		QGL.Compiler.channelLib['q1-gate'].physChan = QGL.Compiler.channelLib['APS1-2m1']
		
		QGL.Compiler.channelLib['q2'].physChan = QGL.Compiler.channelLib['APS1-34']
		QGL.Compiler.channelLib['M-q2'].physChan = QGL.Compiler.channelLib['APS1-34']
		QGL.Compiler.channelLib['M-q2-gate'].physChan = QGL.Compiler.channelLib['APS1-3m1']
		QGL.Compiler.channelLib['q2-gate'].physChan = QGL.Compiler.channelLib['APS1-4m1']

		


if __name__ == "__main__":    
    unittest.main()