"""
Holds all the library instances as the one singleton copy.
"""

import config
from instruments.InstrumentManager import InstrumentLibrary
from QGL.Channels import ChannelLibrary

instrumentLib = InstrumentLibrary(libFile=config.instrumentLibFile)
channelLib = ChannelLibrary(libFile=config.channelLibFile)

