__author__ = 'brayden'

import psutil
from PyQt4 import QtGui
from PyQt4 import QtCore
import os
import sys
import subprocess

class startupScriptSetup(QtGui.QDialog):
    def __init__(self, targetDirectory):
        super(startupScriptSetup, self).__init__()
        self.targetDirectory = targetDirectory
        self.initUI()
    def initUI(self):
        memorySize = psutil.virtual_memory().total / 1024 / 1024
        self.memorySlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        #self.memorySlider.setGeometry(10,10,200,30)
        self.memorySlider.setMaximum(memorySize)
        self.memorySlider.setSingleStep(128)
        self.chosenMemoryIndicator = QtGui.QLabel('Memory (MB): ')
        self.memoryHelpInformation = QtGui.QLabel('The amount of memory you choose dictates how much is\r\n given to the Minecraft server. The amount depends on\r\nserver resources and world size.')
        self.memoryChoosingHintLabel = QtGui.QLabel("Hint: You can use arrow keys\r\nto jump in increments of 128")
        self.enableJavaGarbageCollection = QtGui.QCheckBox('Enable Garbage Collection')
        self.enableJavaGarbageCollection.setChecked(True)
        self.enableJavaGarbageCollectionHelpText = QtGui.QLabel("You should leave this option enabled.\r\nIf you do not your server will crash eventually.")
        self.createScript = QtGui.QPushButton('Create Script')

        grid = QtGui.QGridLayout()
        grid.addWidget(self.memorySlider,1,0)
        grid.addWidget(self.chosenMemoryIndicator,1,1)
        grid.addWidget(self.memoryChoosingHintLabel,2,0)
        grid.addWidget(self.memoryHelpInformation,2,1)
        grid.addWidget(self.enableJavaGarbageCollection,3,0)
        grid.addWidget(self.enableJavaGarbageCollectionHelpText,3,1)
        grid.addWidget(self.createScript,4,0)
        self.memorySlider.connect(self.memorySlider, QtCore.SIGNAL('valueChanged(int)'), self.memorySliderValueChange)
        self.createScript.clicked.connect(self.createScriptButtonClicked)
        self.setLayout(grid)
        self.setWindowTitle('Generate Script')
        self.show()
    def memorySliderValueChange(self, value):
        self.chosenMemoryIndicator.setText('Memory (MB): ' + str(value))
    def createScriptButtonClicked(self):
        # Get Java Path from environment variable, otherwise just use java as the command line and hope it is in the classpath
        if os.name == "nt":
            slash = '\\'
        else:
            slash = '/'
        if not os.getenv('java_home') is None:
            print "Java Home is defined: " + os.getenv('java_home')
            javaPath = '"' + os.getenv('java_home') + 'bin' + slash + 'java.exe' + '"'
            print javaPath
            if not os.path.exists(javaPath.replace('"', '')):
                print "JAVA_HOME is invalid, probably old. Going back to classpath"
                javaPath = 'java'
        else:
            javaPath = 'java' # Hope it is in classpath, can try and test with exit code by using os.system() but cbf
        if self.enableJavaGarbageCollection.isChecked():
            scriptContents = javaPath + " -Xincgc -Xmx" + str(self.memorySlider.value()) + "M -jar craftbukkit.jar"
        else:
            scriptContents = javaPath + " -Xmx" + str(self.memorySlider.value()) + "M -jar craftbukkit.jar"
        print scriptContents
        if os.name == "nt":
            extension = 'bat'
        elif sys.platform == 'darwin':
            extension = 'command'
        else: # In most circumstances this should not be a problem.
            extension = 'sh'
        try:
            with open(self.targetDirectory + "/startserver." + extension, 'w') as script:
                script.write(scriptContents)
        except IOError, e:
            QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), "There was an IOError of some sort.\r\n " + e.message)
        if not os.name == "nt": # On Linux and a lot of other Unix-Likes you have to mark the file executable
            os.system('chmod +x ' + self.targetDirectory + "/startserver." + extension)
        try:
            subprocess.call(javaPath)
            QtGui.QMessageBox.information(self, 'Generate Script Result', 'Script generated successfully.', QtGui.QMessageBox.Ok)
        except OSError:
            QtGui.QMessageBox.critical(self, 'Generate Script Result', 'It appears Java is not installed.')
        self.close()