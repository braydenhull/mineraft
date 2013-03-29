__author__ = 'brayden'

from PyQt4 import QtGui
from PyQt4.QtGui import QMessageBox
from downloadWidget import Downloader
import zipfile
from zipfile import ZipFile
from essentials import Essentials
import os

class essentialsSetupGui(QtGui.QDialog):
    def __init__(self, targetDirectory):
        super(essentialsSetupGui, self).__init__()
        self.targetDirectory = targetDirectory
        self.initUI()

    def initUI(self):
            msg = QMessageBox(self)
            msg.setWindowTitle('Please wait...')
            msg.setIcon(QMessageBox.Information)
            msg.setText('Please wait whilst information is requested.')
            msg.show()
            self.essentialsInformation = Essentials().getInfo('Release')
            #self.essentialsInformation = essentials.Essentials().getInfo('Release')
            msg.close()
            print self.essentialsInformation
            self.pickEssentialsEditionComboBox = QtGui.QComboBox()
            self.pickEssentialsEditionComboBoxLabel = QtGui.QLabel('Select Release: ')
            self.pickEssentialsEditionComboBox.addItems(['Release', 'Pre-Release','Development'])
            self.pickEssentialsVersionComboBox = QtGui.QComboBox()
            self.pickEssentialsVersionComboBoxLabel = QtGui.QLabel('Select Version: ')
            self.pickEssentialsPackageComboBox = QtGui.QComboBox()
            self.pickEssentialsPackageComboBox.addItems(['Full', 'Core', 'Extra', 'GroupManager'])
            self.pickEssentialsPackageComboBoxLabel = QtGui.QLabel('Select Package: ')
            for version in self.essentialsInformation['buildVersions']['version']:
                print version
                self.pickEssentialsVersionComboBox.addItem(version)
            self.downloadEssentialsPlugin = QtGui.QPushButton('Download/Install')

            self.essGrid = QtGui.QGridLayout()
            self.essGrid.addWidget(self.pickEssentialsVersionComboBox,2,2)
            self.essGrid.addWidget(self.pickEssentialsVersionComboBoxLabel,2,1)
            self.essGrid.addWidget(self.pickEssentialsEditionComboBoxLabel,1,1)
            self.essGrid.addWidget(self.pickEssentialsEditionComboBox,1,2)
            self.essGrid.addWidget(self.pickEssentialsPackageComboBoxLabel,3,1)
            self.essGrid.addWidget(self.pickEssentialsPackageComboBox,3,2)
            self.essGrid.addWidget(self.downloadEssentialsPlugin,4,1)
            #self.essGrid.addWidget(self.essentialsInstruction,4,2)
            self.setLayout(self.essGrid)
            self.setWindowTitle('Mineraft - Essentials Setup')
            self.show()
            self.downloadEssentialsPlugin.clicked.connect(self.downloadEssentials)
            self.pickEssentialsEditionComboBox.currentIndexChanged.connect(self.essentialsEditionIndexChange)
    def downloadEssentials(self):
        teamCityBuildIds = {'Release': 'bt3', 'Pre-Release': 'bt9', 'Development': 'bt2', 'GroupManager': 'bt10'}
        essentialsDownloadUrl = Essentials().getDownload(teamCityBuildIds[str(self.pickEssentialsEditionComboBox.currentText())], self.essentialsInformation['buildVersions']['id'][self.pickEssentialsVersionComboBox.currentIndex()], self.pickEssentialsPackageComboBox.currentText())
        print essentialsDownloadUrl
        print self.targetDirectory
        self.dialog = Downloader(essentialsDownloadUrl[0], self.targetDirectory + "/plugins/")
        self.dialog.exec_()
        zipFileName = self.targetDirectory + '/plugins/' + essentialsDownloadUrl[1]
        print zipFileName
        try:
            zipExtraction = ZipFile(zipFileName)
            ZipFile.extractall(zipExtraction, self.targetDirectory + '/plugins')
            ZipFile.close(zipExtraction)
            os.remove(zipFileName)
            self.essentialsCompletedSetupLabel = QtGui.QLabel('Essentials plugin installation complete.')
            self.essentialsCompletedSetupLabel.setStyleSheet('QLabel {color: green}')
            self.essGrid.addWidget(self.essentialsCompletedSetupLabel,5,1)
        except zipfile.BadZipfile, e:
            QtGui.QMessageBox.critical(self, 'Error', 'ZIP file was corrupt.\r\nZipFile said: ' + e.message)
            #QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), 'ZIP file is corrupted.\r\nZipFile said: ' + e.message)
            self.essentialsCompletedSetupLabel = QtGui.QLabel('Essentials failed to install.')
            self.essentialsCompletedSetupLabel.setStyleSheet('QLabel {color: red}')
            self.essGrid.addWidget(self.essentialsCompletedSetupLabel,5,1)

    def essentialsEditionIndexChange(self):
        self.essentialsInformation = Essentials().getInfo(str(self.pickEssentialsEditionComboBox.currentText()))
        self.pickEssentialsVersionComboBox.clear()
        for version in self.essentialsInformation['buildVersions']['version']:
            self.pickEssentialsVersionComboBox.addItem(version)