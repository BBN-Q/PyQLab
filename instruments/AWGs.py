"""
AWGs
"""

from atom.api import Atom, List, Int, Float, Range, Enum, Bool, Constant, Str

from Instrument import Instrument


import enaml
from enaml.qt.qt_application import QtApplication

from AWGBase import AWGChannel, AWG, AWGDriver

from glob import glob
from importlib import import_module
import os
import inspect

AWGList = []

if __name__ == "__main__":


    with enaml.imports():
        from AWGsViews import AWGView

    awg = APS(label='BBNAPS1')
    app = QtApplication()
    view = AWGView(awg=awg)
    view.show()
    app.start()

def find_drivers():
    dirPath = os.path.dirname(__file__)
    searchString = '{0}{1}drivers{2}*.py'.format(dirPath, os.sep, os.sep)
    for file in glob(searchString):
        driverName = file.split(os.sep)[-1].split('.')[0]
        driverName = 'instruments.drivers.' + driverName
        driver = import_module(driverName)
        clsmembers = inspect.getmembers(driver, inspect.isclass)
        # register subclasses of AWG excluding AWG
        for name, clsObj in clsmembers:
            if issubclass(clsObj, AWG) and name != 'AWG':
                AWGList.append(clsObj)
                globals()[clsObj.__name__] = clsObj
                print 'Registered Driver {0}'.format(name)

find_drivers()
