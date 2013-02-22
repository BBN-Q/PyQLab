import sys, os
from pyface.qt import QtGui, QtCore
from PySide import QtUiTools

from instruments.InstrumentManager import InstrumentManager, InstrumentLibraryView
from instruments.MicrowaveSources import AgilentN51853A
from instruments.AWGs import APS

#See http://docs.enthought.com/mayavi/mayavi/auto/example_qt_embedding.html for notes on how to wrap/embed traitsui in vanilla

class ExpSettingsView(QtGui.QMainWindow):
    def __init__(self, settings):
        super(ExpSettingsView, self).__init__()

        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(os.path.join(os.path.dirname(sys.argv[0]), 'ExpSettingsGUI.ui'))
        file.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(file)
        file.close()

        tmpBox = QtGui.QHBoxLayout(self.ui.instrumentTab)
        self.instrumentManager = InstrumentManagerWrapper(settings['instruments'])
        tmpBox.addWidget(self.instrumentManager)
        tmpBox.addStretch(1)

class InstrumentManagerWrapper(QtGui.QWidget):
    """
    Wrap instrument manager in QtWidget.
    """
    def __init__(self, settings):
        super(InstrumentManagerWrapper, self).__init__()
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.manager = InstrumentManager()
        self.manager.load_settings(settings)

        self.ui = self.manager.edit_traits(parent=self, view = InstrumentLibraryView, kind='subpanel').control
        layout.addWidget(self.ui)
        self.ui.setParent(self)

if __name__ == '__main__':
    #Look to see if iPython's event loop is running
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)

    instruments = {}
    instruments['Agilent1'] = AgilentN51853A(name='Agilent1')
    instruments['Agilent2'] = AgilentN51853A(name='Agilent2')
    instruments['BBNAPS1'] = APS(name='BBNAPS1')


    mainWindow = ExpSettingsView({'instruments':instruments})
    mainWindow.ui.show()

    try: 
        from IPython.lib.guisupport import start_event_loop_qt4
        start_event_loop_qt4(app)
    except ImportError:
        sys.exit(app.exec_())



