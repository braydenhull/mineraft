__author__ = 'brayden'
import urllib2
import sys
import re
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QUrl, QFileInfo, QFile, QIODevice
from PyQt4.QtGui import QApplication, QDialog, QProgressBar, QLabel, QPushButton, QDialogButtonBox, \
    QVBoxLayout, QMessageBox, QFileDialog
from PyQt4.QtNetwork import QHttp
from urlparse import urlparse
import os
import zipfile
from zipfile import ZipFile
import psutil
from minecraftQuery import MinecraftQuery
import md5sum
from essentials import Essentials
from plugin import getPlugin
from server import getServer

# This guy is pro http://stackoverflow.com/a/9662362/2077881



nativePluginSupport = ['Essentials']

class pluginSetupGui(QtGui.QDialog):
    def __init__(self, supported, pluginUrl):
        super(pluginSetupGui, self).__init__()
        if not supported:
            self.initUI(pluginUrl)
        elif supported and pluginUrl == 'Essentials':
            self.essentialsSetup()
    def initUI(self, pluginUrl):
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
        global targetDirectory
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
        self.dialog = Downloader(self.downloadInformation['download'], targetDirectory + '/plugins/')
        self.dialog.exec_()
        # this will break if there are parameters on the URL but normally there aren't so it is safe
        zipFileName = targetDirectory + "/plugins/" + self.downloadInformation['download'].split("/")[-1]
        if not md5sum.compute(zipFileName) == self.downloadInformation['MD5']:
            QtGui.QMessageBox.critical(self, 'Error', zipFileName + ' failed MD5 hash check.\r\nDevBukkit: ' + self.downloadInformation['MD5'] + '\r\nFile: ' + md5sum.compute(zipFileName))
            self.close()
        if self.downloadInformation['download'].lower().endswith('.zip'):
            try:
                zipExtraction = ZipFile(zipFileName)
                print zipFileName
                ZipFile.extractall(zipExtraction, targetDirectory + '/plugins/')
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

    def essentialsSetup(self):
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
        global targetDirectory
        teamCityBuildIds = {'Release': 'bt3', 'Pre-Release': 'bt9', 'Development': 'bt2', 'GroupManager': 'bt10'}
        essentialsDownloadUrl = Essentials().getDownload(teamCityBuildIds[str(self.pickEssentialsEditionComboBox.currentText())], self.essentialsInformation['buildVersions']['id'][self.pickEssentialsVersionComboBox.currentIndex()], self.pickEssentialsPackageComboBox.currentText())
        print essentialsDownloadUrl
        print targetDirectory
        self.dialog = Downloader(essentialsDownloadUrl[0], targetDirectory + "/plugins/")
        self.dialog.exec_()
        zipFileName = targetDirectory + '/plugins/' + essentialsDownloadUrl[1]
        print zipFileName
        try:
            zipExtraction = ZipFile(zipFileName)
            ZipFile.extractall(zipExtraction, targetDirectory + '/plugins')
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

class startupScriptSetup(QtGui.QDialog):
    def __init__(self):
        super(startupScriptSetup, self).__init__()
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
        global targetDirectory
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
            with open(targetDirectory + "/startserver." + extension, 'w') as script:
                script.write(scriptContents)
        except IOError, e:
            QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), "There was an IOError of some sort.\r\n " + e.message)
        if not os.name == "nt": # On Linux and a lot of other Unix-Likes you have to mark the file executable
            os.system('chmod +x ' + targetDirectory + "/startserver." + extension)
        QtGui.QMessageBox.information(self, 'Generate Script Result', 'Script generated successfully.', QtGui.QMessageBox.Ok)
        self.close()

class managerGui(QtGui.QDialog):
    def __init__(self):
        super(managerGui, self).__init__()
        self.initUI()
    def initUI(self):
        global targetDirectory
        targetDirectory = ''
        msg = QMessageBox(self)
        msg.setWindowTitle('Please wait...')
        msg.setIcon(QMessageBox.Information)
        msg.setText('Please wait whilst information is requested.')
        msg.show()
        self.cacheBukkitRecommendedResultInfo = getServer().getRecommendedBukkitInfo()
        msg.close()
        self.getBukkit = QtGui.QPushButton('Get Craftbukkit')
        self.bukkitEditions = QtGui.QComboBox(self)
        self.bukkitEditions.addItems(['Recommended', 'Beta', 'Development'])
        self.bukkitVersions = QtGui.QComboBox(self)
        self.bukkitVersionsLabel = QtGui.QLabel('Build: ' + str(self.cacheBukkitRecommendedResultInfo['results'][0]['build_number']))
        for result in self.cacheBukkitRecommendedResultInfo['results']:
            self.bukkitVersions.addItem(result['version'])
        self.setupStartupScriptButton = QtGui.QPushButton('Create Startup Script')
        self.startServer = QtGui.QPushButton('Start Server')


        self.pluginOfficialSupportComboBox = QtGui.QComboBox(self)
        self.pluginOfficialSupportComboBox.addItems(nativePluginSupport)
        self.pluginOfficialSupportComboBoxLabel = QtGui.QLabel("Natively Supported Plugins:")
        self.pluginCustomPluginUrlLabel = QtGui.QLabel("BukkitDev Plugins:")
        self.pluginCustomPluginUrl = QtGui.QLineEdit("http://dev.bukkit.org/server-mods/Essentials/")
        self.installPluginButton = QtGui.QPushButton("Setup Dev Bukkit Plugin")
        self.installSupportedPluginButton = QtGui.QPushButton("Setup Natively Supported Plugin")

        self.browseInstallDirectoryButton = QtGui.QPushButton("Browse...")
        self.browseInstallDirectoryButtonLabel = QtGui.QLabel("This is required before you install plugins")
        self.browseInstallDirectoryButtonLabel.setStyleSheet('QLabel {color: red}')

        # Status widgets
        self.statusIpAddress = QtGui.QLineEdit('127.0.0.1')
        self.statusIpAddressLabel = QtGui.QLabel('IP: ')
        self.statusPortNumber = QtGui.QLineEdit('25565')
        self.statusPortNumberLabel = QtGui.QLabel('Port: ')
        self.statusRefreshButton = QtGui.QPushButton('Refresh')
        self.statusConnectedPlayers = QtGui.QListWidget()
        self.statusConnectedPlayersLabel = QtGui.QLabel('Connected Players')
        self.statusInstalledPlugins = QtGui.QListWidget()
        self.statusInstalledPluginsLabel = QtGui.QLabel('Installed Plugins')
        self.statusMinecraftVersion = QtGui.QLabel('Version: ')
        self.statusMaxPlayers = QtGui.QLabel('Max Players: ')

        bukkitGrid = QtGui.QGroupBox("Bukkit")
        self.bukkitGridLayout = QtGui.QVBoxLayout()
        self.bukkitGridLayout.setSpacing(10)
        self.bukkitGridLayout.addWidget(self.getBukkit,1)
        self.bukkitGridLayout.addWidget(self.bukkitEditions,2)
        self.bukkitGridLayout.addWidget(self.bukkitVersions,3)
        self.bukkitGridLayout.addWidget(self.bukkitVersionsLabel,4)
        self.bukkitGridLayout.addWidget(self.setupStartupScriptButton,5)
        self.bukkitGridLayout.addWidget(self.startServer,6)

        pluginGrid = QtGui.QGroupBox("Plugin")
        pluginGridLayout = QtGui.QVBoxLayout()
        pluginGridLayout.setSpacing(10)
        pluginGridLayout.addWidget(self.pluginOfficialSupportComboBoxLabel,1)
        pluginGridLayout.addWidget(self.pluginOfficialSupportComboBox,2)
        pluginGridLayout.addWidget(self.installSupportedPluginButton,3)
        pluginGridLayout.addWidget(self.pluginCustomPluginUrlLabel,4)
        pluginGridLayout.addWidget(self.pluginCustomPluginUrl,5)
        pluginGridLayout.addWidget(self.installPluginButton,6)

        bukkitGrid.setLayout(self.bukkitGridLayout)
        pluginGrid.setLayout(pluginGridLayout)

        self.grid = QtGui.QGridLayout()
        self.grid.addWidget(self.browseInstallDirectoryButton,1,0)
        self.grid.addWidget(self.browseInstallDirectoryButtonLabel,1,1)
        self.grid.addWidget(bukkitGrid,2,0)
        self.grid.addWidget(pluginGrid,2,1)

        self.grid.addWidget(self.statusIpAddressLabel,3,0)
        self.grid.addWidget(self.statusIpAddress,3,1)
        self.grid.addWidget(self.statusPortNumberLabel,4,0)
        self.grid.addWidget(self.statusPortNumber,4,1)
        self.grid.addWidget(self.statusConnectedPlayersLabel,5,0)
        self.grid.addWidget(self.statusConnectedPlayers,6,0)
        self.grid.addWidget(self.statusInstalledPluginsLabel,5,1)
        self.grid.addWidget(self.statusInstalledPlugins,6,1)
        self.grid.addWidget(self.statusMaxPlayers,7,0)
        self.grid.addWidget(self.statusMinecraftVersion,7,1)
        self.grid.addWidget(self.statusRefreshButton,8,0)

        # grid.setSpacing(10)
        # grid.addWidget(self.getBukkit,1,0)
        # grid.addWidget(self.bukkitEditions,2,0)
        # grid.addWidget(self.bukkitVersions,3,0)
        # grid.addWidget(self.bukkitVersionsLabel,4,0)

        self.setLayout(self.grid)
        self.setWindowTitle('Mineraft')
        self.show()
        self.getBukkit.clicked.connect(self.getBukkitButtonPress)
        self.bukkitEditions.currentIndexChanged.connect(self.bukkitEditionIndexChange)
        self.bukkitVersions.currentIndexChanged.connect(self.bukkitVersionsIndexChange)
        self.installPluginButton.clicked.connect(self.installPluginButtonPress)
        self.installSupportedPluginButton.clicked.connect(self.installSupportedPluginButtonPress)
        self.browseInstallDirectoryButton.clicked.connect(self.browseInstallDirectoryButtonClick)
        self.statusRefreshButton.clicked.connect(self.refreshStatus)
        self.setupStartupScriptButton.clicked.connect(self.setupStartupScriptButtonClick)
        self.startServer.clicked.connect(self.startServerButtonClick)

    def startServerButtonClick(self):
        global targetDirectory
        if not targetDirectory == "":
            if os.name == "nt":
                extension = '.bat'
            elif sys.platform == 'darwin':
                extension = '.command'
            else:
                extension = '.sh'
            os.chdir(targetDirectory)
            if os.name == 'nt':
                os.system('start ' + targetDirectory + '/startserver' + extension)
            elif sys.platform == 'darwin':
                os.system('open ' + targetDirectory + '/startserver' + extension)
            else:
                os.system('xterm ' + targetDirectory + '/startserver' + extension)
        else:
            #QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), 'Please select a directory first.')
            QtGui.QMessageBox.critical(self, 'Error', 'Please select a directory first.')

    def setupStartupScriptButtonClick(self):
        global targetDirectory
        if not targetDirectory == "":
            self.dialog = startupScriptSetup()
            self.dialog.exec_()
            if os.name == 'nt':
                extension = '.bat'
            else:
                extension = '.sh'
            if os.path.isfile(targetDirectory + '/startserver' + extension):
                try:
                    if self.startupFileInfo is None:
                        self.startupFileInfo = QtGui.QLabel('startserver' + extension + ' is present.')
                        self.startupFileInfo.setStyleSheet('QLabel {color: green}')
                        self.bukkitGridLayout.addWidget(self.startupFileInfo,7)
                except AttributeError:
                    self.startupFileInfo = QtGui.QLabel('startserver' + extension + ' is present.')
                    self.startupFileInfo.setStyleSheet('QLabel {color: green}')
                    self.bukkitGridLayout.addWidget(self.startupFileInfo,7)
        else:
            QtGui.QMessageBox.critical(self, 'Error', 'Please select a directory first.')

    def installSupportedPluginButtonPress(self):
        global targetDirectory
        if not targetDirectory == '':
            self.dialog = pluginSetupGui(True, self.pluginOfficialSupportComboBox.currentText())
            self.dialog.exec_()
        else:
            QtGui.QMessageBox.critical(self, 'Error', 'Please select a directory first.')
    def installPluginButtonPress(self):
        global targetDirectory
        if not targetDirectory == '':
            self.dialog = pluginSetupGui(False, self.pluginCustomPluginUrl.text())
            self.dialog.exec_()
        else:
            QtGui.QMessageBox.critical(self, 'Error', 'Please select a directory first.')
    def getBukkitButtonPress(self):
        global targetDirectory
        print targetDirectory
        if not targetDirectory == '':
            targetDirectory += '/'
            if not self.bukkitVersions.currentText() == '':
                realUrl = ''
                if self.bukkitEditions.currentText() == 'Recommended':
                    print "Download URL is: http://dl.bukkit.org" + self.cacheBukkitRecommendedResultInfo['results'][self.bukkitVersions.currentIndex()]['file']['url']
                    realUrl = urllib2.urlopen('http://dl.bukkit.org' + self.cacheBukkitRecommendedResultInfo['results'][self.bukkitVersions.currentIndex()]['file']['url'])
                    print realUrl.url
                    self.dialog = Downloader(realUrl.url, targetDirectory)
                elif self.bukkitEditions.currentText() == 'Beta':
                    print "Download URL is: http://dl.bukkit.org" + self.cacheBukkitBetaResultInfo['results'][self.bukkitVersions.currentIndex()]['file']['url']
                    realUrl = urllib2.urlopen('http://dl.bukkit.org' + self.cacheBukkitBetaResultInfo['results'][self.bukkitVersions.currentIndex()]['file']['url'])
                    self.dialog = Downloader(realUrl.url, targetDirectory)
                elif self.bukkitEditions.currentText() == 'Development':
                    print "Download URL is: http://dl.bukkit.org" + self.cacheBukkitDevResultInfo['results'][self.bukkitVersions.currentIndex()]['file']['url']
                    realUrl = urllib2.urlopen('http://dl.bukkit.org' + self.cacheBukkitDevResultInfo['results'][self.bukkitVersions.currentIndex()]['file']['url'])
                    self.dialog = Downloader(realUrl.url, targetDirectory)
                self.dialog.exec_()
                fileName = realUrl.url.split("/")[-1]
                print fileName
                if os.path.isfile(targetDirectory + '/craftbukkit.jar'):
                    os.remove(targetDirectory + '/craftbukkit.jar')
                os.rename(targetDirectory + '/' + fileName, targetDirectory + '/craftbukkit.jar')
        else:
            QtGui.QMessageBox.critical(self, 'Error', 'Please select a directory first.')
    def bukkitEditionIndexChange(self):
        self.bukkitVersions.clear()
        if self.bukkitEditions.currentText() == 'Recommended':
            #self.cacheBukkitRecommendedResultInfo = getServer().getRecommendedBukkitInfo()
            for result in self.cacheBukkitRecommendedResultInfo['results']:
                self.bukkitVersions.addItem(result['version'])
        elif self.bukkitEditions.currentText() == 'Beta':
            self.cacheBukkitBetaResultInfo = getServer().getBetaBukkitInfo()
            for result in self.cacheBukkitBetaResultInfo['results']:
                self.bukkitVersions.addItem(result['version'])
        elif self.bukkitEditions.currentText() == 'Development':
            self.cacheBukkitDevResultInfo = getServer().getDevBukkitInfo()
            for result in self.cacheBukkitDevResultInfo['results']:
                self.bukkitVersions.addItem(result['version'])
    def bukkitVersionsIndexChange(self):
        print("Index is " + str(self.bukkitVersions.currentIndex()))
        if self.bukkitEditions.currentText() == 'Recommended':
            try:
                self.bukkitVersionsLabel.setText("Build: " + str(self.cacheBukkitRecommendedResultInfo['results'][self.bukkitVersions.currentIndex()]['build_number']))
            except AttributeError:
                pass
        elif self.bukkitEditions.currentText() == 'Beta':
            try:
                self.bukkitVersionsLabel.setText("Build: " + str(self.cacheBukkitBetaResultInfo['results'][self.bukkitVersions.currentIndex()]['build_number']))
            except AttributeError:
                pass
        elif self.bukkitEditions.currentText() == 'Development':
            try:
                self.bukkitVersionsLabel.setText("Build: " + str(self.cacheBukkitDevResultInfo['results'][self.bukkitVersions.currentIndex()]['build_number']))
            except AttributeError:
                pass
    def browseInstallDirectoryButtonClick(self):
        global targetDirectory
        targetDirectory = str(QFileDialog.getExistingDirectory(self, "Select Target Directory"))
        if os.path.exists(targetDirectory):
            if not os.path.exists(targetDirectory + "/plugins/"):
                os.makedirs(targetDirectory + "/plugins/")
            self.browseInstallDirectoryButtonLabel.setText('Directory is valid!')
            self.browseInstallDirectoryButtonLabel.setStyleSheet('QLabel {color: green}')
            if os.name == 'nt':
                extension = '.bat'
            elif sys.platform == 'darwin':
                extension = '.command'
            else:
                extension = '.sh'
            if os.path.isfile(targetDirectory + '/startserver' + extension):
                self.startupFileInfo = QtGui.QLabel('startserver' + extension + ' is present.')
                self.startupFileInfo.setStyleSheet('QLabel {color: green}')
                self.bukkitGridLayout.addWidget(self.startupFileInfo,7)
        else: # This really should not happen unless they press cancel
            self.browseInstallDirectoryButtonLabel.setStyleSheet('QLabel {color: red}')
            self.browseInstallDirectoryButtonLabel.setText('Selected directory does not exist.')
    def refreshStatus(self):
        self.minecraftQuery = MinecraftQuery(self.statusIpAddress.text(), self.statusPortNumber.text())
        self.minecraftQueryInformation = self.minecraftQuery.get_rules()
        self.statusMaxPlayers.setText('Max Players: ' + str(self.minecraftQueryInformation['maxplayers']))
        self.statusMinecraftVersion.setText('Version: ' + self.minecraftQueryInformation['version'])
        # If you forget to clear the list then all the items double up
        self.statusInstalledPlugins.clear()
        self.statusInstalledPlugins.addItems(self.minecraftQueryInformation['plugins'])
        self.statusConnectedPlayers.clear()
        self.statusConnectedPlayers.addItems(self.minecraftQueryInformation['players'])

# Thanks to this guy for this whole thing, pretty much, http://stackoverflow.com/a/6856810/2077881
class Downloader(QDialog):
    def __init__(self, url_to_download, directory, parent=None):
        super(Downloader, self).__init__(parent)

        self.targetDirectory = directory
        self.downloadUrl = url_to_download
        self.httpGetId = 0
        self.httpRequestAborted = False
        self.statusLabel = QLabel('Downloading %s' % url_to_download)
        self.closeButton = QPushButton("Close")
        self.closeButton.setAutoDefault(False)
        self.progressBar = QProgressBar()

        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self.closeButton, QDialogButtonBox.RejectRole)

        self.http = QHttp(self)
        self.http.requestFinished.connect(self.httpRequestFinished)
        self.http.dataReadProgress.connect(self.updateDataReadProgress)
        self.http.responseHeaderReceived.connect(self.readResponseHeader)
        self.closeButton.clicked.connect(self.cancelDownload)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.statusLabel)
        mainLayout.addWidget(self.progressBar)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle('Download')
        self.downloadFile()

    def downloadFile(self):
        url = QUrl(self.downloadUrl)
        fileInfo = QFileInfo(url.path())
        #fileName = fileInfo.fileName()
        fileName = self.targetDirectory + fileInfo.fileName()
        if QFile.exists(fileName):
            QFile.remove(fileName)
        self.outFile = QFile(fileName)
        if not self.outFile.open(QIODevice.WriteOnly):
            QMessageBox.information(self, 'Error', 'Unable to save the file %s: %s.' % (fileName, self.outFile.errorString()))
            self.outFile = None
            return
        mode = QHttp.ConnectionModeHttp
        port = url.port()
        if port == -1:
            port = 0
        self.http.setHost(url.host(), mode, port)
        self.httpRequestAborted = False
        print url
        path = QUrl.toPercentEncoding(url.path(), "!$&'()*+,;=:@/")
        if path:
            path = str(path)
        else:
            path = '/'
        # Right at the end we append the query string that is lost, the original author did not include this unfortunately.
        parsedUrl = urlparse(self.downloadUrl)
        if not parsedUrl.query == '':
            # fix this mess, otherwise leave it alone
            path = path + "?" + parsedUrl.query
            print path
        # Download the file.
        self.httpGetId = self.http.get(path, self.outFile)
    def cancelDownload(self):
        self.statusLabel.setText("Download canceled.")
        self.httpRequestAborted = True
        self.http.abort()
        self.close()
    def httpRequestFinished(self, requestId, error):
        if requestId != self.httpGetId:
            return
        if self.httpRequestAborted:
            if self.outFile is not None:
                self.outFile.close()
                self.outFile.remove()
                self.outFile = None
            return
        self.outFile.close()
        if error:
            self.outFile.remove()
            QMessageBox.information(self, 'Error','Download failed: %s.' % self.http.errorString())
        self.statusLabel.setText('Done')

    def readResponseHeader(self, responseHeader):
        # Check for genuine error conditions.
        if responseHeader.statusCode() not in (200, 300, 301, 302, 303, 307):
            QMessageBox.information(self, 'Error', 'Download failed: %s.' % responseHeader.reasonPhrase())
            self.httpRequestAborted = True
            self.http.abort()
    def updateDataReadProgress(self, bytesRead, totalBytes):
        if self.httpRequestAborted:
            return
        self.progressBar.setMaximum(totalBytes)
        self.progressBar.setValue(bytesRead)
def main():
    app = QtGui.QApplication(sys.argv)
    ex = managerGui()
    sys.exit(app.exec_())

main()