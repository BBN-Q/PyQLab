import sys, os
from pyface.qt import QtGui, QtCore
from PySide import QtUiTools

from instruments.InstrumentManager import InstrumentManager
from instruments.MicrowaveSources import AgilentN51853A
from instruments.AWGs import APS

class ExpSettingsView(QtGui.QMainWindow):
    def __init__(self, settings):
        super(ExpSettingsView, self).__init__()

        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(os.path.join(os.path.dirname(sys.argv[0]), 'ExpSettingsGUI.ui'))
        file.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(file)
        file.close()

        tmpBox = QtGui.QHBoxLayout(self.ui.instrumentTab)
        self.instrumentManager = InstrumentManager(settings['instruments'])
        tmpBox.addWidget(self.instrumentManager)
        tmpBox.addStretch(1)



if __name__ == '__main__':
    #Look to see if iPython's event loop is running
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)

    instruments = {}
    instruments['Agilent1'] = AgilentN51853A()
    instruments['Agilent2'] = AgilentN51853A()
    instruments['BBNAPS1'] = APS()


    mainWindow = ExpSettingsView({'instruments':instruments})
    mainWindow.ui.show()

    try: 
        from IPython.lib.guisupport import start_event_loop_qt4
        start_event_loop_qt4(app)
    except ImportError:
        sys.exit(app.exec_())



