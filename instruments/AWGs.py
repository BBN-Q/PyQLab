"""
AWGs
"""

from traits.api import Str, Int, Float, Bool, Enum

from Instrument import Instrument

import enaml
from enaml.stdlib.sessions import show_simple_view

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

AWGList = [APS, Tek5014]

if __name__ == "__main__":

	with enaml.imports():
		from AWGView import AWGView
	
	awg = APS(name='BBNAPS1')
	session = show_simple_view(AWGView(awg=awg))
