__author__ = 'brayden'

from PyQt4 import QtGui
from PyQt4.QtGui import QMessageBox, QLabel
from plugin import getPlugin
from downloadWidget import Downloader
import md5sum
import zipfile
from zipfile import ZipFile
from essentials import Essentials
import os
from essentialsSetupWidget import essentialsSetupGui


class pluginSetupGui(QtGui.QDialog):
    def __init__(self, supported, pluginUrl, targetDirectory):
        super(pluginSetupGui, self).__init__()
        print targetDirectory
        self.targetDirectory = targetDirectory
        if not supported:
            self.initUI(pluginUrl, supported)
        # elif supported and pluginUrl == 'Essentials':
        #     self.dialog = essentialsSetupGui(targetDirectory)
        #     self.dialog.exec_()
    def initUI(self, pluginUrl, supported):
        msg = QMessageBox(self)
        msg.setWindowTitle('Please wait...')
        msg.setIcon(QMessageBox.Information)
        msg.setText('Please wait whilst information is requested.')
        msg.show()
        self.pluginInformation = getPlugin().getGenericBukkitDevPluginInfo(str(pluginUrl))
        msg.close()
        self.pickVersionComboBox = QtGui.QComboBox()
        for version in self.pluginInformation['versions']['title']:
            self.pickVersionComboBox.addItem(version)

        self.versionDescription = QtGui.QTextEdit()
        self.versionDescription.setText(self.pluginInformation['versions']['description'][0])
        self.downloadPlugin = QtGui.QPushButton("Download/Install")
        self.downloadUrlLabel = QtGui.QLabel('URL')
        self.md5HashLabel = QtGui.QLabel('MD5')
        self.supportedCB = QtGui.QLabel('CB: ')

        self.grid = QtGui.QGridLayout()
        self.grid.addWidget(self.pickVersionComboBox,1,1)
        self.grid.addWidget(self.versionDescription,2,1)
        self.grid.addWidget(self.downloadPlugin,3,1)
        self.grid.addWidget(self.downloadUrlLabel,4,1)
        self.grid.addWidget(self.md5HashLabel,5,1)
        self.grid.addWidget(self.supportedCB,6,1)


        self.setLayout(self.grid)
        self.setWindowTitle('Mineraft - Plugin Setup')
        self.show()
        self.pickVersionComboBox.currentIndexChanged.connect(self.pickVersionComboBoxIndexChange)
        self.downloadPlugin.clicked.connect(self.downloadPluginButtonPress)
    def pickVersionComboBoxIndexChange(self):
        self.versionDescription.clear()
        self.versionDescription.setText(self.pluginInformation['versions']['description'][self.pickVersionComboBox.currentIndex()])
    def downloadPluginButtonPress(self):
        msg = QMessageBox(self)
        msg.setWindowTitle('Please wait...')
        msg.setIcon(QMessageBox.Information)
        msg.setText('Please wait whilst information is requested.')
        msg.show()
        self.downloadInformation = getPlugin().getGenericBukkitDevPluginDownloadInformation(self.pluginInformation['versions']['link'][self.pickVersionComboBox.currentIndex()])
        msg.close()
        self.downloadUrlLabel.setText('URL: ' + self.downloadInformation['download'])
        self.md5HashLabel.setText('MD5: ' + self.downloadInformation['MD5'])
        self.supportedCB.setText('CB: ' + ", ".join(self.downloadInformation['supportedCraftBukkit']))
        #self.supportedCB.setText('CB: '+ str(self.downloadInformation['supportedCraftBukkit']))
        self.dialog = Downloader(self.downloadInformation['download'], self.targetDirectory + '/plugins/')
        self.dialog.exec_()
        # this will break if there are parameters on the URL but normally there aren't so it is safe
        zipFileName = self.targetDirectory + "/plugins/" + self.downloadInformation['download'].split("/")[-1]
        if not md5sum.compute(zipFileName) == self.downloadInformation['MD5']:
            QtGui.QMessageBox.critical(self, 'Error', zipFileName + ' failed MD5 hash check.\r\nDevBukkit: ' + self.downloadInformation['MD5'] + '\r\nFile: ' + md5sum.compute(zipFileName))
            self.close()
        if self.downloadInformation['download'].lower().endswith('.zip'):
            try:
                zipExtraction = ZipFile(zipFileName)
                print zipFileName
                ZipFile.extractall(zipExtraction, self.targetDirectory + '/plugins/')
                ZipFile.close(zipExtraction)
                os.remove(zipFileName)
                self.completedSetupLabel = QLabel("Plugin setup complete.")
                self.completedSetupLabel.setStyleSheet('QLabel {color: green}')
                self.grid.addWidget(self.completedSetupLabel,7,1)
            except zipfile.BadZipfile:
                QtGui.QMessageBox.critical(self, 'Error', 'ZIP file was corrupt.')
                self.completedSetupLabel = QLabel("Plugin setup failed.")
                self.completedSetupLabel.setStyleSheet('QLabel {color: red}')
                self.grid.addWidget(self.completedSetupLabel,7,1)
        QtGui.QMessageBox.information(self, 'Success', 'Plugin installed successfully.')
        self.close()
