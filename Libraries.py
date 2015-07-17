"""
Holds all the library instances as the one singleton copy.
"""
import h5py #bonus h5py import for issue https://github.com/BBN-Q/PyQLab/issues/26
import config
from instruments.InstrumentManager import InstrumentLibrary
from QGL.Channels import ChannelLibrary
from Sweeps import SweepLibrary
from MeasFilters import MeasFilterLibrary
import LibraryMigrator

migrationMsg = LibraryMigrator.migrate_all()
for msg in migrationMsg:
    print msg

instrumentLib = InstrumentLibrary(libFile=config.instrumentLibFile)
channelLib = ChannelLibrary(libFile=config.channelLibFile)
sweepLib = SweepLibrary(libFile=config.sweepLibFile)
measLib = MeasFilterLibrary(libFile=config.measurementLibFile)

