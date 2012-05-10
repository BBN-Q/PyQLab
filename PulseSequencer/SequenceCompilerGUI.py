"""

Main GUI for compiling sequences

Created on Wed May  9 17:53:11 2012

@author: cryan

"""
import sys
from PySide import QtGui, QtCore

from PulseSequencer import compile_sequences, logical2hardware
from TekPattern import write_Tek_file

import ChannelInfo


class SequenceCompilerGUI(QtGui.QMainWindow):
    
    def __init__(self):
        super(SequenceCompilerGUI, self).__init__()
        self.initUI()

    def initUI(self):

        self.setGeometry(300,300,800,500)
        self.setWindowTitle('BBN Sequence Compiler')


        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        
        compileAction = QtGui.QAction('Compile',self)
        compileAction.setStatusTip('Compile Sequence')
        compileAction.triggered.connect(self.compile_sequence)
        

        #Setup the menus
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        #Setup the toolbar
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(compileAction)

        self.statusBar()

        self.sequenceEdit = QtGui.QTextEdit() 
        font = QtGui.QFont("Courier", 11)
        font.setFixedPitch(True)
        self.sequenceEdit.setFont(font)
        self.setCentralWidget(self.sequenceEdit)

        self.setTabPosition( QtCore.Qt.RightDockWidgetArea , QtGui.QTabWidget.North )
        self.setDockOptions( QtGui.QMainWindow.ForceTabbedDocks )

        messageDock = QtGui.QDockWidget('Message Log')
        self.messageLog = QtGui.QTextEdit()
        messageDock.setWidget(self.messageLog)
        messageDock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, messageDock)
 
        paramsDock = QtGui.QDockWidget('Sequence Parameters')
        self.paramsTable = QtGui.QTableWidget(100,2)
        self.paramsTable.setHorizontalHeaderLabels(['Parameter', 'Value'])
        paramsDock.setWidget(self.paramsTable)
        paramsDock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, paramsDock)
 
        self.tabifyDockWidget(messageDock, paramsDock)

        self.show()
        
        
    def compile_sequence(self):
        
        '''
        Put together the sequence and compile it to AWG files.

        Basic steps are:
        1) Evaluate the parameters
        2) Concatenate the header, parameter, sequence and tail files together and execute it
        
        This whole thing is hacky but it's worked for years for me. 
        '''
        
        self.headerFile = 'sequence.h'        
        
        #Execute the file (obviously this is somewhat dangerous)
        exec(compile(open(self.headerFile).read(), self.headerFile, 'exec'), locals())
        exec(compile(self.sequenceEdit.toPlainText(), '', 'exec'), locals())        
        
        #We should now have access to a list of pulseSeqs
        LLs, WFLibrary = compile_sequences(pulseSeqs)  
        AWGWFs = logical2hardware(LLs, WFLibrary, channelInfo)
    
        self.messageLog.append('Writing Tek File...')
        write_Tek_file(AWGWFs['TekAWG1'], 'silly.awg', 'silly')
        self.messageLog.append('Done writing Tek File.')


        
            

if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    mainWindow = SequenceCompilerGUI()
    sys.exit(app.exec_())