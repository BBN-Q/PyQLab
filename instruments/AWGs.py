"""
AWGs
"""

from traits.api import Str, Int, Float, Bool, Enum
from traitsui.api import View, Item, HGroup

from Instrument import Instrument

class AWG(Instrument):
	pass

class APS(AWG):
	name = Str
	address = Str('', desc='address of unit as serial number', label='Address')
	triggerSource = Enum('Internal', 'External', desc='source of trigger', label='Trigger Source')
	triggerInterval = Float(1e-4, desc='internal trigger interval', label='Trigger Int.')
	samplingRate = Float(1200, desc='sampling rate in MHz', label='Sampling Rate')
    
class Tek5014(AWG):
	pass

