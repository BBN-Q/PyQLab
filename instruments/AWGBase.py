"""
AWGs
"""

from atom.api import Atom, List, Int, Float, Range, Enum, Bool, Constant, Str

from .Instrument import Instrument

import enaml
from enaml.qt.qt_application import QtApplication

import glob
import copy

class AWGDriver:
    naming_convention = []

    def get_naming_convention(self):
        # return copy of empty_channel_set so different AWGs will not share memory
        return copy.copy(self.naming_convention)

class AWGChannel(Atom):
    label = Str()
    amplitude = Float(default=1.0).tag(desc="Scaling applied to channel amplitude")
    offset = Float(default=0.0).tag(desc='D.C. offset applied to channel')
    enabled = Bool(True).tag(desc='Whether the channel output is enabled.')

class AWG(Instrument, AWGDriver):
    isMaster = Bool(False).tag(desc='Whether this AWG is master')
    triggerSource = Enum('Internal', 'External').tag(desc='Source of trigger')
    triggerInterval = Float(1e-4).tag(desc='Internal trigger interval')
    samplingRate = Float(1200000000).tag(desc='Sampling rate in Hz')
    numChannels = Int()
    channels = List(AWGChannel)
    seqFile = Str().tag(desc='Path to sequence file.')
    seqFileExt = Constant('')
    seqForce = Bool(True).tag(desc='Whether to reload the sequence')
    delay = Float(0.0).tag(desc='time shift to align multiple AWGs')
    translator = Constant('')

    def __init__(self, **traits):
        super(AWG, self).__init__(**traits)
        if not self.channels:
            for ct in range(self.numChannels):
                self.channels.append(AWGChannel())

    def json_encode(self, matlabCompatible=False):
        jsonDict = super(AWG, self).json_encode(matlabCompatible)

        # Skip encoding of constants
        del jsonDict["seqFileExt"]
        del jsonDict["translator"]

        if matlabCompatible:
            channels = jsonDict.pop('channels', None)
            for ct,chan in enumerate(channels):
                jsonDict['chan_{}'.format(ct+1)] = chan
        return jsonDict

    def update_from_jsondict(self, params):
        for ct in range(self.numChannels):
            channelParams = params['channels'][ct]

            # if this is still a raw dictionary convert to object
            if isinstance(channelParams, dict):
                channelParams.pop('x__class__', None)
                channelParams.pop('x__module__', None)
                channelParams = AWGChannel(**channelParams)

            self.channels[ct].label = channelParams.label
            self.channels[ct].amplitude = channelParams.amplitude
            self.channels[ct].offset = channelParams.offset
            self.channels[ct].enabled = channelParams.enabled

        for p in ['label', 'enabled', 'address', 'isMaster', 'triggerSource', 'triggerInterval', 'samplingRate', 'seqFile', 'seqForce', 'delay']:
            setattr(self, p, params[p])
