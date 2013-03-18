"""
Various sweeps for scanning experiment parameters
"""

from traits.api import HasTraits, Str, Float, Int, Bool, Dict, List, \
	Instance, Property, Array, cached_property, TraitListObject
import enaml

from instruments.MicrowaveSources import MicrowaveSource
from instruments.Instrument import Instrument

import abc
import numpy as np

class Sweep(HasTraits):
	name = Str
	label = Str
	numSteps = Int
	enabled = Bool(True)
	possibleInstrs = Instance(TraitListObject)

	@abc.abstractmethod
	def step(self, index):
		pass

	def get_stack_view(self):
		with enaml.imports():
			from SweepsViews import SweepStackView
		return SweepStackView(mySweep=self, possibleInstrs=self.possibleInstrs)

class PointsSweep(Sweep):
	"""
	A class for sweeps with floating points with one instrument
	"""
	start = Float
	stop = Float
	step = Float
	points = Property(depends_on=['start', 'stop', 'step'])

	@cached_property
	def _get_points(self):
		return np.arange(self.start, self.stop, self.step)

class Power(PointsSweep):
	label = 'Power'
	instr = Instance(MicrowaveSource)

class Frequency(PointsSweep):
	label = 'Frequency'
	instr = Instance(MicrowaveSource)

class SegmentNum(PointsSweep):
	pass

class SweepLibrary(HasTraits):
	sweepDict = Dict(Str, Sweep)
	sweepList = Property(List, depends_on='sweepDict')
	newSweepClasses = List([Power, Frequency])
	possibleInstrs = List(Instrument)

	@cached_property
	def _get_sweepList(self):
		return [sweep.name for sweep in self.sweepDict.values() if sweep.enabled]

if __name__ == "__main__":

	from instruments.MicrowaveSources import AgilentN51853A	
	testSource1 = AgilentN51853A(name='TestSource1')
	testSource2 = AgilentN51853A(name='TestSource2')

	from Sweeps import Frequency, Power, SweepLibrary
	sweepLib = SweepLibrary(possibleInstrs=[testSource1, testSource2])
	sweepLib.sweepDict.update({'TestSweep1':Frequency(name='TestSweep1', start=5, stop=6, step=0.1, instr=testSource1, possibleInstrs=sweepLib.possibleInstrs)})
	sweepLib.sweepDict.update({'TestSweep2':Power(name='TestSweep2', start=-20, stop=0, step=0.5, instr=testSource2, possibleInstrs=sweepLib.possibleInstrs)})

	from enaml.stdlib.sessions import show_simple_view

	with enaml.imports():
		from SweepsViews import SweepManagerWindow
	session = show_simple_view(SweepManagerWindow(sweepLib=sweepLib))
