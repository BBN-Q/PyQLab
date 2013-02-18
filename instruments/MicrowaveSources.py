from traits.api import Str, Int, Float, Bool, Enum
from traitsui.api import View, Item, VGroup, HGroup, spring

from Instrument import Instrument

class MicrowaveSource(Instrument):
    name = Str
    address = Str('', desc='address of unit as GPIB or I.P.', label='Address')
    power = Float(0.0, desc='output power in dBm', label='Output Power')
    frequency = Float(5.0, desc='frequency in GHz', label='Frequency')
    modulate = Bool(False, desc='whether output is modulated', label='Modulate')
    alc = Bool(False, desc='whether automatic level control is on', label='ALC')

MicrowaveSourceView = View(VGroup(
            Item(name = 'address'),
            Item(name = 'power'),
            Item(name = 'frequency'),
            HGroup(Item(name = 'alc', enabled_when='not modulate'),
            Item(name = 'modulate'),
            Item(name = 'pulseModulate', enabled_when='modulate')),
            Item(name = 'pulseModSource', enabled_when='modulate'), spring), resizable=True)

class AgilentN51853A(MicrowaveSource):
	pulseModulate = Bool(False, desc='whether pulse modulation is on', label='Pulse Mod.')
	pulseModSource = Enum('Internal', 'External', desc='source of pulse modulation', label='Pulse Mod. Source')

if __name__ == "__main__":

	uwSource = AgilentN51853A()
	uwSource.configure_traits(view=MicrowaveSourceView)

