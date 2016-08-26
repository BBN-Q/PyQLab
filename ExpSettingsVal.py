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

from builtins import str
import floatbits
import itertools
import re

import h5py
from atom.api import Str

import Sweeps
import Libraries
import QGL.Channels
import QGL.ChannelLibrary


channels = QGL.ChannelLibrary.channelLib
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
#    2 LogicalMarkerChannel must map to PhysicalMarkerChannel
#   3 Not LogicalMarkerChannel not map to PhysicalMarkerChannel
#
# Physical Channels:
#   1 PhysicalChannel must have an AWG assigned
#     2 The assigned AWG must exist in the library
#    3 The name of the PhysicalChannel channel must be of the form AWGName-AWGChannel
#   4 Device specific naming conventions
#     APS: 12, 34, 1m1, 2m1, 3m1, 4m1
#     APS2: 12, 12m1, 12m2, 12m3, 12m4
#     Tek5014: 12, 34, 1m1, 1m2, 2m1, 2m2, 3m1, 3m2, 4m1, 4m2
#
# Instruments Names:
#   1 Instrument names must be valid Matlab Identifiers

# Conventions to be added
#
#

#####################################################################################
## Program Constants

# Matlab valid identifier -- Starts with a letter, followed by letters, digits, or underscores.
# Maximum length is the return value from the namelengthmax function
# namelengthmax returned 63 on Matlab 2015a 64-bit linux
MATLAB_NAME_LENGTH_MAX = 63
MATLAB_FORMAT_STRING = "\A[a-zA-Z]\w{0,%i}?\Z" % (MATLAB_NAME_LENGTH_MAX - 1)
MATLAB_VALID_NAME_REGEX = re.compile(MATLAB_FORMAT_STRING)

#####################################################################################
## Helper functions for list comprehension

def is_logicalmarker_channel(name):
    return is_channel_type(name, QGL.Channels.LogicalMarkerChannel)

def is_physical_channel(name):
    return is_channel_type(name, QGL.Channels.PhysicalChannel)

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
    return isinstance(channels[name], channelType)


#####################################################################################
### Apply global rules

def test_require_physical():
    """Enforces rule requiring physical channels for certain logical channels

       See requires_physical_channel() for list of Channel types requiring a
       Physical channel.
    """
    errors = []
    channels = QGL.ChannelLibrary.channelLib
    testChannels = [channelName for channelName in channels.keys() if requires_physical_channel(channelName)]

    for channel in testChannels:
        physicalChannel = channels[channel].physChan

        if physicalChannel is None:
            errMsg = '"{0}" channel "{1}" Physical Channel is not defined'.format(channels[channel].__class__.__name__, channel)
            errors.append(errMsg)
        else:
            physicalChannelName = channels[channel].physChan.label
            if physicalChannelName not in channels.keys():
                errMsg =  'Physical Channel "{0}" not found'.format(physicalChannelName)
                errors.append(errMsg)

    return errors

## Apply invidual test based on channel type
def test_logical_channels():
    """
        Enforces rules applied against logical channels

        These are rules in addition to those applied at the global level.

        Rules:
        PhysicalChannel but be in library
        "Markerness" of logical and physical channels must match, i.e.
        LogicalMarkerChannel must map to PhysicalMarkerChannel.
    """
    errors = []
    channels = QGL.ChannelLibrary.channelLib

    # require all LogicalMarkerChannels to map to PhysicalMarkerChannels
    # and require all not LogicalMarkerChannels to map to not PhysicalMarkerChannels
    logicalChannels = [channelName for channelName in channels.keys() if requires_physical_channel(channelName)]

    for channel in logicalChannels:
        errorHeader = '{0} Markerness of {1} and {2} do not match'
        if not channels[channel].physChan:
            continue
        physicalChannelName = channels[channel].physChan.label
        if physicalChannelName not in channels.keys():
            continue
        if is_logicalmarker_channel(channel) != is_physicalmarker_channel(physicalChannelName):
            errMsg =  errorHeader.format(channels[channel].__class__.__name__, channel, physicalChannelName)
            errors.append(errMsg)

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

    channels = QGL.ChannelLibrary.channelLib
    physicalChannels = [channelName for channelName in channels.keys() if is_physical_channel(channelName)]

    for channel in physicalChannels:
        awg = channels[channel].AWG
        if awg == '':
            errMsg = 'Physical Channel "{0}" requires an AWG assignment'.format(channel)
            errors.append(errMsg)
        elif awg not in instruments.keys():
            errMsg =  'Physical Channel "{0}" AWG {1} not found'.format(channel, awg)
            errors.append(errMsg)

        # test AWG name to channel format
        validName = True
        validName &= '-' in channel
        if validName:
            awgName, awgChan = channel.rsplit('-',1)
            if awgName not in instruments.keys():
                errMsg =  'Physical Channel "{0}" Label format is invalid. It should be Name-Channel'.format(channel)
                errors.append(errMsg)
            if awgName != awg:
                errMsg =  'Physical Channel "{0}" Label AWGName {1} != AWG.label {2}'.format(channel, awgName, awg)
                errors.append(errMsg)

            # apply device specific channel namming conventions
            # force converions of awgChan to unicode so multimethod dispatch will
            # work with str or unicode
            errMsg = invalid_awg_name_convention(channels[channel].AWG, str(awgChan))
            if errMsg:
                errors.append(errMsg)
        else:
            errMsg =  'Physical Channel "{0}" Label format is invalid. It should be Name-Channel'.format(channel)
            errors.append(errMsg)

    return errors

#####################################################################################
## AWG Model Type naming conventions
def invalid_awg_name_convention_common(label, channelName, conventionList):
    errorStr =  'AWG {0} channel name {1} not in convention list {2}'
    if channelName not in conventionList:
        return errorStr.format(label, channelName, conventionList)
    return None

def invalid_awg_name_convention(awgLabel, channelName):
    AWG = instruments[awgLabel]
    convention = AWG.get_naming_convention()
    return invalid_awg_name_convention_common(awgLabel, channelName,convention)

# GUI validator
def is_valid_awg_channel_name(channelName):
    if '-' in channelName:
        awgName, awgChan = channelName.rsplit('-',1)
    else:
        awgName = channelName

    if awgName not in instruments.keys():
        return False
    return (invalid_awg_name_convention(awgName, awgChan) is None)

#####################################################################################

def is_valid_instrument_name(label):
    # instrument must be a valid Matlab identifier
    return (MATLAB_VALID_NAME_REGEX.match(label) is not None)

def validate_instrumentLib():

    errors = []

    invalidNames = [instrument for instrument in instruments.keys() if not is_valid_instrument_name(instrument)]

    if invalidNames != []:
        for name in invalidNames:
            errMsg =  "Instrument name {0} is not a valid Matlab Name".format(name)
            errors.append(errMsg)

    return errors
#####################################################################################

def validate_sweepLib():
    errors = []

    for key in sweeps.keys():
        if isinstance(sweeps[key],Sweeps.PointsSweep):
            try:
                numPoints = int((sweeps[key].stop - sweeps[key].start)/floatbits.prevfloat(sweeps[key].step)) + 1
            except ValueError as e:
                errors.append("Sweep named %s issue computing Num. Points: %s" % (sweeps[key].label,e))

    return errors


#####################################################################################

def validate_channelLib():
    errors = []
    if 'digitizerTrig' not in channels.keys():
        errMsg = 'A LogicalMarkerChannel named digitizerTrig is required'
        errors.append([errMsg])

    # test gate pulses

    if 'slaveTrig' not in channels.keys():
        errMsg = 'A LogicalMarkerChannel named slaveTrig is required'
        errors.append([errMsg])

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

    errors = list(itertools.chain(*errors))
    return errors

def validate_dynamic_lib(channelsLib, instrumentLib):
    global channels
    global instruments
    channels = channelsLib
    instruments = instrumentLib.instrDict
    return validate_lib()

def validate_lib():
    errors = []

    channel_errors = validate_channelLib()
    if channel_errors != []:
        errors.append(channel_errors)

    instrument_errors = validate_instrumentLib()
    if instrument_errors != []:
        errors.append(instrument_errors)

    sweep_errors = validate_sweepLib()
    if sweep_errors != []:
       errors.append(sweep_errors)

    errors = list(itertools.chain(*errors))
    return errors

def default_repr(items, item):
    return '\t{0}: {1}'.format(item,
                            items[item].__class__.__name__)

def default_list_repr(items, name):
    print("Listing available {}:".format(name))
    for item in items.keys():
        print(default_repr(items,item))

def list_channels():
    print("Listing available channels:")
    for channel in channels.keys():
        print("\t", repr(channels[channel]))

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

    print("digraph Exp {")

    for channel in topLevelChannels:
        print('"{}"'.format(channel))
        if channels[channel].physChan is not None:
            print(' -> "{}"'.format(channels[channel].physChan.label))
            if channels[channel].physChan.AWG is not None:
                print(' -> "{}"'.format(channels[channel].physChan.AWG.label))

    typeMap = (
        (is_logicalmarker_channel,"lightblue"),
        (is_physicalmarker_channel,"red"),
        (is_physicalIQ_channel,"blue"),
        (is_qubit_channel,"yellow"),
        )

    for lookup, color in typeMap:
        names = [channelName for channelName in channels.keys() if lookup(channelName)]
        for channel in names:
            print("{0} [color={1},style=filled];".format(channel, color))

    instrumentNames = [channelName for channelName in instruments.keys()]
    for channel in instrumentNames:
        print("{} [color=green,style=filled];".format(channel))

    print("}")


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
        error = validate_lib()
        print(error)

    if args.list:
        list_config()
