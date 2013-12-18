"""
AWGs
"""

from atom.api import Atom, List, Int, Float, Range, Enum, Bool, Constant, Str

from Instrument import Instrument

import enaml
from enaml.qt.qt_application import QtApplication


class AWGChannel(Atom):
    label = Str()
    amplitude = Float(default=1.0).tag(desc="Scaling applied to channel amplitude")
    offset = Float(default=0.0).tag(desc='D.C. offset applied to channel')
    enabled = Bool(True).tag(desc='Whether the channel output is enabled.')

class AWG(Instrument):
    isMaster = Bool(False).tag(desc='Whether this AWG is master')
    triggerSource = Enum('Internal', 'External').tag(desc='Source of trigger')
    triggerInterval = Float(1e-4).tag(desc='Internal trigger interval')
    samplingRate = Float(1200000000).tag(desc='Sampling rate in Hz')
    numChannels = Int()
    channels = List(AWGChannel)
    seqFile = Str().tag(desc='Path to sequence file.')
    seqForce = Bool(True).tag(desc='Whether to reload the sequence')
    delay = Float(0.0).tag(desc='time shift to align multiple AWGs')

    def __init__(self, **traits):
        super(AWG, self).__init__(**traits)
        if not self.channels:
            for ct in range(self.numChannels):
                self.channels.append(AWGChannel())

    def json_encode(self, matlabCompatible=False):
        jsonDict = super(AWG, self).json_encode(matlabCompatible)

        #The seq file extension is constant so don't encode
        del jsonDict["seqFileExt"]

        if matlabCompatible:
            channels = jsonDict.pop('channels', None)
            for ct,chan in enumerate(channels):
                jsonDict['chan_{}'.format(ct+1)] = chan
        return jsonDict

class APS(AWG):
    numChannels = Int(default=4)
    miniLLRepeat = Int(0).tag(desc='How many times to repeat each miniLL')
    seqFileExt = Constant('.h5')

class Tek5014(AWG):
    numChannels = Int(default=4)
    seqFileExt = Constant('.awg')

class Tek7000(AWG):
    numChannels = Int(default=2)
    seqFileExt = Constant('.awg')

AWGList = [APS, Tek5014, Tek7000]

if __name__ == "__main__":

    with enaml.imports():
        from AWGViews import AWGView
    
    awg = APS(label='BBNAPS1')
    app = QtApplication()
    view = AWGView(awg=awg)
    view.show()
    app.start()


def get_empty_channel_set(AWG):
    """
    Helper function to get the set of empty channels when compiling to hardware.
    """
    if isinstance(AWG, Tek5014):
        return {'ch12':{}, 'ch34':{}, 'ch1m1':{}, 'ch1m2':{}, 'ch2m1':{}, 'ch2m2':{}, 'ch3m1':{}, 'ch3m2':{} , 'ch4m1':{}, 'ch4m2':{}}
    elif isinstance(AWG, Tek7000):
        return {'ch12':{}, 'ch1m1':{}, 'ch1m2':{}, 'ch2m1':{}, 'ch2m2':{}}
    elif isinstance(AWG, APS):
        return {'ch12':{}, 'ch34':{}, 'ch1m1':{}, 'ch2m1':{}, 'ch3m1':{}, 'ch4m1':{}}
    else:
        raise NameError('Unknown AWG type')             

