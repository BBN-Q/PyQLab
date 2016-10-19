"""
For now just Alazar cards but should also support Acquiris.
"""
from .Instrument import Instrument

from atom.api import Atom, Str, Int, Float, Bool, Enum, List, Dict, Coerced
import itertools, ast

import enaml
from enaml.qt.qt_application import QtApplication

class Digitizer(Instrument):
	takes_marker = True
	naming_convention = []

	def get_naming_convention(self):
		return self.naming_convention

class ATS9870(Digitizer):
	naming_convention = ['1', '2']
	address           = Str('1').tag(desc='Location of the card') #For now we only have one
	acquire_mode      = Enum('digitizer', 'averager').tag(desc='Whether the card averages on-board or returns single-shot data')
	clock_type        = Enum('ref')
	delay             = Float(0.0).tag(desc='Delay from trigger')
	sampling_rate     = Float(100000000).tag(desc='Sampling rate in Hz')
	vertical_scale    = Float(1.0).tag(desc='Peak voltage (V)')
	vertical_offset   = Float(0.0).tag(desc='Vertical offset (V)')
	vertical_coupling = Enum('AC','DC').tag(desc='AC/DC coupling')
	bandwidth         = Enum('20MHz', 'Full').tag(desc='Input bandwidth filter')
	trigger_level     = Float(0.0).tag(desc='Trigger level (mV)')
	trigger_source    = Enum('A','B','Ext').tag(desc='Trigger source')
	trigger_coupling  = Enum('AC','DC').tag(desc='Trigger coupling')
	trigger_slope     = Enum('rising','falling').tag(desc='Trigger slope')
	record_length     = Int(1024).tag(desc='Number of samples in each record')
	nbr_segments      = Int(1).tag(desc='Number of segments in memory')
	nbr_waveforms     = Int(1).tag(desc='Number of times each segment is repeated')
	nbr_round_robins  = Int(1).tag(desc='Number of times entire memory is looped')

class X6(Digitizer):
	naming_convention = ['1', '2']
	record_length      = Int(1024).tag(desc='Number of samples in each record')
	nbr_segments       = Int(1).tag(desc='Number of segments in memory')
	nbr_waveforms      = Int(1).tag(desc='Number of times each segment is repeated')
	nbr_round_robins   = Int(1).tag(desc='Number of times entire memory is looped')
	enable_raw_streams = Bool(False).tag(desc='Enable capture of raw data from ADCs')

	digitizer_mode     = Enum('digitizer', 'averager').tag(desc='Whether the card averages on-board or returns single-shot data')
	reference          = Enum('external', 'internal').tag(desc='Clock source for 10MHz reference to clock generation tree')

if __name__ == "__main__":
	from Digitizers import X6
	digitizer = X6(label='scope')
	with enaml.imports():
		from DigitizersViews import TestX6Window

		app = QtApplication()
	view = TestX6Window(instr=digitizer)
	view.show()
	app.start()
