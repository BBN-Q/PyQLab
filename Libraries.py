"""
Holds all the library instances as the one singleton copy.
"""
import h5py #bonus h5py import for issue https://github.com/BBN-Q/PyQLab/issues/26
import config
from instruments.InstrumentManager import InstrumentLibrary
from Sweeps import SweepLibrary
from MeasFilters import MeasFilterLibrary
from JSONLibraryUtils import JSONMigrators

migrationMsg = JSONMigrators.migrate_all(config)
for msg in migrationMsg:
    print msg

instrumentLib = InstrumentLibrary(libFile=config.instrumentLibFile)
sweepLib = SweepLibrary(libFile=config.sweepLibFile)
measLib = MeasFilterLibrary(libFile=config.measurementLibFile)
