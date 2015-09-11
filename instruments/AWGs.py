"""
AWGs
"""

from atom.api import Atom, List, Int, Float, Range, Enum, Bool, Constant, Str

from Instrument import Instrument


import enaml
from enaml.qt.qt_application import QtApplication

from instruments.AWGBase import AWGChannel, AWG, AWGDriver

from plugins import find_plugins

AWGList = []

plugins = find_plugins(AWG)
for plugin in plugins:
    AWGList.append(plugin)
    globals().update({plugin.__name__: plugin})
    print 'Registered AWG Driver {0}'.format(plugin.__name__)

if __name__ == "__main__":


    with enaml.imports():
        from AWGsViews import AWGView

    awg = APS(label='BBNAPS1')
    app = QtApplication()
    view = AWGView(awg=awg)
    view.show()
    app.start()
