"""
Various sweeps for scanning experiment parameters
"""

from traits.api import HasTraits, Str, Float, Int, Bool, \
	Instance, Property, Array, cached_property

from instruments.MicrowaveSources import MicrowaveSource

import abc
import numpy as np


class Sweep(HasTraits):
	name = Str
	label = Str
	numSteps = Int
	enabled = Bool(True)

	@abc.abstractmethod
	def step(self, index):
		pass

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


if __name__ == "__main__":

	from instruments.MicrowaveSources import AgilentN51853A	
	testSource1 = AgilentN51853A(name='TestSource1')
	testSource2 = AgilentN51853A(name='TestSource2')
	testSweep1 = Frequency(name='TestSweep1', start=5, stop=6, step=0.1, instr=testSource1)
	testSweep2 = Power(name='TestSweep2', start=-20, stop=0, step=0.5, instr=testSource2)

	import enaml
	from enaml.stdlib.sessions import show_simple_view

	with enaml.imports():
		from SweepsViews import SweepManagerWindow
	session = show_simple_view(SweepManagerWindow(sweeps=[testSweep1, testSweep2], possibleInstrs=[testSource1, testSource2]))
