"""
AWGs
"""

from traits.api import HasTraits, List, Int, Float, Range, Bool, Enum, File

from Instrument import Instrument

import enaml
from enaml.stdlib.sessions import show_simple_view


class AWGChannel(HasTraits):
    amplitude = Range(value=1.0, low=0.0, high=1.0, desc="Scaling applied to channel amplitude")
    offset = Range(value=0.0, low=-1.0, high=1.0, desc='D.C. offset applied to channel')
    enabled = Bool(True, desc='Whether the channel output is enabled.')

class AWG(Instrument):
    isMaster = Bool(False, desc='Whether this AWG is master')
    triggerSource = Enum('Internal', 'External', desc='Source of trigger')
    triggerInterval = Float(1e-4, desc='Internal trigger interval')
    samplingRate = Float(1200000000, desc='Sampling rate in Hz')
    numChannels = Int()
    channels = List(AWGChannel)
    seqFile = File(desc='Path to sequence file.')
    seqForce = Bool(True, desc='Whether to reload the sequence')
    delay = Float(0.0, desc='time shift to align multiple AWGs')

    def __init__(self, **traits):
        super(AWG, self).__init__(**traits)
        if not self.channels:
            for ct in range(self.numChannels):
                self.channels.append(AWGChannel(name='Chan. {}'.format(ct+1)))

class APS(AWG):
    numChannels = 4
    miniLLRepeat = Int(0, desc='How many times to repeat each miniLL')

class Tek5014(AWG):
    numChannels = 4

class Tek7000(AWG):
    numChannels = 2

AWGList = [APS, Tek5014, Tek7000]

if __name__ == "__main__":

    with enaml.imports():
        from AWGViews import AWGView
    
    awg = APS(name='BBNAPS1')
    session = show_simple_view(AWGView(awg=awg))


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

