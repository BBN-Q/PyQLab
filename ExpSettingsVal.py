'''
ExpSettingsVal - 
Validates Experimental Settings against a set of rules known to cause 
the Compiler (Compiler.py) to fail if they are not followed

Created on April 17, 2015

Original Author: Brian Donovan

Copyright 2015 Raytheon BBN Technologies

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import h5py
import Libraries
import QGL.Channels

from QGL.mm import multimethod
from instruments.AWGs import APS, APS2, Tek5014

from atom.api import Str

channels = Libraries.channelLib.channelDict
instruments = Libraries.instrumentLib.instrDict
measurements = Libraries.measLib.filterDict
sweeps = Libraries.sweepLib.sweepDict

# The following naming conventions are currently enforced
# See: https://github.com/BBN-Q/PyQLab/wiki
#
# Two LogicalMarkerChannels are required:
#   1 digitizerTrig
#   2 slaveTrig
#
# Logical Channels: 
#   1 PhysicalChannel but be in library
#	2 LogicalMarkerChannel must map to PhysicalMarkerChannel
#
# Physical Channels:
#   1 PhysicalChannel must have an AWG assigned
# 	2 The assigned AWG must exist in the library
#	3 The name of the PhysicalChannel channel must be of the form AWGName-AWGChannel
#   4 Device specific naming conventions
#     APS: 12, 34, 1m1, 2m1, 3m1, 4m1
#     APS2: 12, 12m1, 12m2, 12m3, 12m4
#     Tek5014: 12, 34, 1m1, 1m2, 2m1, 2m2, 3m1, 3m2, 4m1, 4m2

# Conventions to be added
# 
#

#####################################################################################
## Helper functions for list comprehension 

def is_logicalmarker_channel(name):
	return is_channel_type(name, QGL.Channels.LogicalMarkerChannel)	

def is_physicalmarker_channel(name):
	return is_channel_type(name, QGL.Channels.PhysicalMarkerChannel)	

def is_physicalIQ_channel(name):
	return is_channel_type(name, QGL.Channels.PhysicalQuadratureChannel)	

def is_qubit_channel(name):
	return is_channel_type(name, QGL.Channels.Qubit)	

def is_measurement_channel(name):
	return is_channel_type(name, QGL.Channels.Measurement)	

def requires_physical_channel(name):
	return is_channel_type(name, QGL.Channels.LogicalChannel) 

def is_channel_type(name, channelType):
	channels = Libraries.channelLib.channelDict
	return isinstance(channels[name], channelType)	

#####################################################################################
### Apply global rules

def test_require_physical():
	"""Enforces rule requiring physical channels for certain logical channels

	   See requires_physical_channel() for list of Channel types requiring a
	   Physical channel.
	"""
	errors = []
	channels = Libraries.channelLib.channelDict
	testChannels = [channelName for channelName in channels.keys() if requires_physical_channel(channelName)]

	for channel in testChannels:
		physicalChannel = channels[channel].physChan

		if physicalChannel is None:
			print '"{0}" channel "{1}" Physical Channel is not defined'.format(channels[channel].__class__.__name__, channel)
			errors.append(channel)

	return errors

## Apply invidual test based on channel type
def test_logical_channels():
	"""
		Enforces rules applied against logical channels

		These are rules in addition to those applied at the global level.

		Rules:
		PhysicalChannel but be in library
		LogicalMarkerChannel must map to PhysicalMarkerChannel
	"""
	errors = []
	channels = Libraries.channelLib.channelDict
	logicalChannels = [channelName for channelName in channels.keys() if is_logicalmarker_channel(channelName)]
	
	for channel in logicalChannels:
		if not is_logicalmarker_channel(channel):
			continue
		errorHeader = 'LogicalMarkerChannel "{0}" requires a Physical Marker Channel'.format(channel)
		if channels[channel].physChan is not None:
			physicalChannelName = channels[channel].physChan.label
			if physicalChannelName not in channels.keys():
				print errorHeader
				print '\tPhysical Channel "{0}" not found'.format(physicalChannelName)
				errors.append(physicalChannelName)
			elif not is_physicalmarker_channel(physicalChannelName):
				print channels[channel].physChan
				print '\tChannel "{0}" is not a Physical Marker Channel'.format(physicalChannelName)
				errors.append(physicalChannelName)
	return errors

def test_physical_channels():
	"""
		Enforces rules applied against physical channels

		Rules:
		PhysicalChannel must have an AWG assigned
		The assigned AWG must exist in the library
		The name of the PhysicalChannel channel must be of the form AWGName-AWGChannel
		Device channels have model specific naming conventions
	"""
	errors = []
	channels = Libraries.channelLib.channelDict
	physicalChannels = [channelName for channelName in channels.keys() if is_physicalmarker_channel(channelName)]

	for channel in physicalChannels:
		awg = channels[channel].AWG.label
		if awg == '':
			print 'Physical Channel "{0}" requires an AWG assignment'.format(channel)
			errors.append(channel)
		elif awg not in instruments.keys():
			print 'Physical Channel "{0}" AWG {1} not found'.format(channel, awg)
			errors.append(channel)

		# test AWG name to channel format
		validName = True
		validName &= '-' in channel
		if validName:
			awgName, awgChan = channel.split('-')
			if awgName not in instruments.keys():
				print 'Physical Channel "{0}" Label format is invalid. It should be Name-Channel'.format(channel)				
				errors.append(channel)
			if awgName != awg:
				print 'Physical Channel "{0}" Label AWGName {1} != AWG.label {2}'.format(channel, awgName, awg)
				errors.append(channel)
			
			# apply device specific channel namming conventions
			# force converions of awgChan to unicode so multimethod dispatch will
			# work with str or unicode
			if invalid_awg_name_convention(channels[channel].AWG, unicode(awgChan)):
				errors.append(channel)
		else:
			print 'Physical Channel "{0}" Label format is invalid. It should be Name-Channel'.format(channel)				
			errors.append(channel)

	return errors

#####################################################################################
## AWG Model Type naming conventions
def invalid_awg_name_convention_common(label, channelName, conventionList):
	errorStr =  'AWG {0} channel name {1} not in convention list {2}'
	if channelName not in conventionList:
		print errorStr.format(label, channelName, conventionList)
		return True
	return False

@multimethod(APS, unicode)
def invalid_awg_name_convention(AWG, channelName):
	convention = ['12', '34', '1m1', '2m1', '3m1', '4m1']
	return invalid_awg_name_convention_common(AWG.label, channelName,convention)

@multimethod(APS2, unicode)
def invalid_awg_name_convention(AWG, channelName):
	convention = ['12', '12m1', '12m2', '12m3', '12m4']
	return invalid_awg_name_convention_common(AWG.label, channelName,convention)

@multimethod(Tek5014, unicode)
def invalid_awg_name_convention(AWG, channelName):
	convention = ['12', '34', '1m1', '1m2', '2m1', '2m2', '3m1', '3m2', '4m1', '4m2']
	return invalid_awg_name_convention_common(AWG.label, channelName,convention)

#####################################################################################

def validate_channelLib():
	errors = []
	if 'digitizerTrig' not in channels.keys():
		print 'A LogicalMarkerChannel named digitizerTrig is required'
		errors.append('digitizerTrig')
			
	# test gate pulses

	if 'slaveTrig' not in channels.keys():
		print 'A LogicalMarkerChannel named slaveTrig is required'
		errors.append('slaveTrig')		

	# test map_logical_to_physical
	rp_errors = test_require_physical()
	pc_errors = test_physical_channels()
	lc_errors = test_logical_channels()

	if pc_errors != []:
		errors.append(pc_errors)
	if lc_errors != []:		
		errors.append(lc_errors)
	if rp_errors != []:		
		errors.append(rp_errors)		

	print errors
	return errors

def validate_lib():
	if validate_channelLib() != []:
		return False
	return True

def default_repr(items, item):
	return '\t{0}: {1}'.format(item, 
							items[item].__class__.__name__)

def default_list_repr(items, name):
	print 'Listing available {0}:'.format(name)
	for item in items.keys():
		print default_repr(items,item)

def list_channels():
	print 'Listing available channels:'
	for channel in channels.keys():
		print '\t', repr(channels[channel])

def list_instruments():
	default_list_repr(instruments, 'instruments')
	
def list_measurements():
	default_list_repr(measurements, 'measurements')
	
def list_sweeps():
	default_list_repr(sweeps, 'sweeps')
		

def list_config():
	list_channels()
	print
	list_instruments()
	print
	list_measurements()
	print
	list_sweeps()

def draw_wiring_digram():

	topLevelChannels = [channelName for channelName in channels.keys() if requires_physical_channel(channelName)]

	print "digraph Exp {"

	for channel in topLevelChannels:
		print '"{0}"'.format(channel), 
		if channels[channel].physChan is not None:
			print ' -> "{0}"'.format(channels[channel].physChan.label),
			if channels[channel].physChan.AWG is not None:
				print ' -> "{0}"'.format(channels[channel].physChan.AWG.label),
		print

	typeMap = (
		(is_logicalmarker_channel,"lightblue"),
		(is_physicalmarker_channel,"red"),
		(is_physicalIQ_channel,"blue"),
		(is_qubit_channel,"yellow"),
		)

	for type in typeMap:
		lookup, color = type
		names = [channelName for channelName in channels.keys() if lookup(channelName)]
		for channel in names:
			print '"{0}" [color={1},style=filled];'.format(channel, color)

	instrumentNames = [channelName for channelName in instruments.keys()]
	for channel in instrumentNames:
		print '"{0}" [color=green,style=filled];'.format(channel)		

	print "}"


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('-d', dest='draw_digram', action='store_true')
	parser.add_argument('-v', dest='validate', action='store_true')
	parser.add_argument('-l', dest='list', action='store_true')

	args = parser.parse_args()
	
	if args.draw_digram:
		draw_wiring_digram()

	if args.validate:
		validate_lib()

	if args.list:
		list_config()
