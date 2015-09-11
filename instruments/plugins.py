"""
Device driver pluggins
"""
from glob import glob
from importlib import import_module
import os
import inspect

class PluginViewMap(object):
    viewMap = {}
    viewType = object

def isStrictSubclass( clsObj, baseClass):
    return issubclass(clsObj, baseClass) and clsObj.__name__ != baseClass.__name__

def find_view_maps(baseClass, viewMap):
    def addToMap(newMap):
        keys = newMap.viewMap.keys()
        if newMap.viewType.__name__ != baseClass.__name__:
            print "Not mapping", newMap.viewType.__name__,' to ', baseClass.__name__
            return
        filterMap = {key:newMap.viewMap[key] for key in keys if isStrictSubclass(key, baseClass)}
        viewMap.update(filterMap.items())

    for plugin in find_plugins(PluginViewMap):
        addToMap(plugin)

def find_plugins(baseClass):
    plugins = []
    dirPath = os.path.dirname(__file__)
    searchString = '{0}{1}drivers{2}*.py'.format(dirPath, os.sep, os.sep)
    for file in glob(searchString):
        driverName = file.split(os.sep)[-1].split('.')[0]
        driverName = 'instruments.drivers.' + driverName
        driver = import_module(driverName)
        clsmembers = inspect.getmembers(driver, inspect.isclass)
        # register subclasses of AWG excluding AWG
        for name, clsObj in clsmembers:
            if isStrictSubclass(clsObj, baseClass):
                plugins.append(clsObj)
                print 'Registered Driver {0}'.format(name)
    return plugins
                
