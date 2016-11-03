"""
AWGs
"""

from atom.api import Atom, List, Int, Float, Range, Enum, Bool, Constant, Str

from .Instrument import Instrument


import enaml
from enaml.qt.qt_application import QtApplication

from instruments.AWGBase import AWGChannel, AWG, AWGDriver

from .plugins import find_plugins

AWGList = []

# local plugin registration to enable access by AWGs.plugin
plugins = find_plugins(AWG, verbose=False)
for plugin in plugins:
    if plugin not in AWGList:
        AWGList.append(plugin)
        if plugin.__name__ not in globals().keys():
            globals().update({plugin.__name__: plugin})
            print("Registered Plugin {}".format(plugin.__name__))

if __name__ == "__main__":
    with enaml.imports():
        from AWGsViews import AWGView

    awg = APS(label='BBNAPS1')
    app = QtApplication()
    view = AWGView(awg=awg)
    view.show()
    app.start()
