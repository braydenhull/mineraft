__author__ = 'brayden'
import json
import urllib2
import sys
from bs4 import BeautifulSoup
import re
import feedparser
from PyQt4 import QtGui, QtCore
#from PyQt4.QtCore import *
from PyQt4.QtCore import QUrl, QFileInfo, QFile, QIODevice
from PyQt4.QtGui import QApplication, QDialog, QProgressBar, QLabel, QPushButton, QDialogButtonBox, \
    QVBoxLayout, QMessageBox, QFileDialog
from PyQt4.QtNetwork import QHttp
from urlparse import urlparse
import os
import zipfile
from zipfile import ZipFile
#from minecraftQuery import MinecraftQuery
import psutil
import socket
import struct

# This guy is pro http://stackoverflow.com/a/9662362/2077881
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

nativePluginSupport = ['Essentials']

class Essentials():
    def getInfo(self, version):
        teamCityBuildIds = {'Release': 'bt3', 'Pre-Release': 'bt9', 'Development': 'bt2', 'GroupManager': 'bt10'} # I can get this sort of info manually but it'd take some hacky URL parsing and is liable to break so I feel this is better
        # The compiled list of everything that should be needed for Essentials. this is quite a lot of info though but I don't want to have to call this function more than once
        # Build artifacts is unfilled as I don't know why I put it there
        essInfo = {'buildVersions': {'id': [],'version': []}, 'buildArtifacts': [], 'buildType': teamCityBuildIds[version]}
        try:
            buildTypeId = teamCityBuildIds[version]
            print buildTypeId
        except IndexError:
            print("Version string given is not known.")
            sys.exit(1)
        request = urllib2.Request('http://ess.ementalo.com/guestAuth/app/rest/buildTypes/id:' + buildTypeId + '/builds', headers={"Accept": "application/json"})
        buildList = json.loads(urllib2.urlopen(request).read())
        print buildList
        print "Versions available: "
        for build in buildList['build']:
            print(build)
            print("Essentials stable " + build['number'] + " is available.")
            essInfo['buildVersions']['version'].append(build['number'])
            essInfo['buildVersions']['id'].append(build['id'])
        return essInfo

    def getDownload(self, buildTypeId, buildId, edition):
        if edition ==  'Extra':
            fileName = 'Essentials-extra.zip'
        elif edition == 'Full':
            fileName = 'Essentials-full.zip'
        elif edition == 'Core':
            fileName = 'Essentials.zip'
        elif edition == 'GroupManager':
            fileName = 'Essentials-gm.zip'
        else:
            print "Edition was not valid, options are: Extra, Full, Core or GroupManager."
            print "Setting Edition to Core as a contingency"
            fileName = 'Essentials.zip'
        url = 'http://ess.ementalo.com/repository/download/' + buildTypeId + '/' + str(buildId) + ':id/' + fileName + '?guest=1' # If you don't do ?guest=1 it'll not work properly!
        return url, fileName
class getPlugin():
    def getGenericBukkitDevPluginInfo(self, pluginUrl):
        print "got this far!"
        returnInfoDict = {'versions': {'title': [], 'description': [], 'link': []}}
        feed = feedparser.parse(pluginUrl + 'files.rss')
        for entry in feed['entries']:
            returnInfoDict['versions']['title'].append(entry['title'])
            returnInfoDict['versions']['description'].append(remove_tags(entry['summary_detail']['value']))
            returnInfoDict['versions']['link'].append(entry['links'][0]['href'])
        # generate exception so I get memory footprint
        #doesnotexist[1]
        return returnInfoDict
    def getGenericBukkitDevPluginDownloadInformation(self, url):
        returnInfoDict = {'download': '', 'MD5': '', 'supportedCraftBukkit': []}
        request = urllib2.Request(url)
        webpage = BeautifulSoup(urllib2.urlopen(request).read())
        for link in webpage.find_all('a', href=re.compile('^http://dev.bukkit.org/media/files/')):
            returnInfoDict['download'] = link.get('href')
            break
        returnInfoDict['MD5'] = webpage.find("dt",text="MD5").findNextSiblings("dd")[0].string
        for tagContent in webpage.find('ul',{"class": "comma-separated-list"}).find_all('li'):
            returnInfoDict['supportedCraftBukkit'].append(tagContent.string)
        return returnInfoDict
class getServer():
    def getRecommendedBukkitInfo(self):
        request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/artifacts/rb/?_accept=application%2Fjson')
        buildList = json.loads(urllib2.urlopen(request).read())
        return buildList
    def getBetaBukkitInfo(self):
        request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/artifacts/beta/?_accept=application%2Fjson')
        buildList = json.loads(urllib2.urlopen(request).read())
        return buildList
    def getDevBukkitInfo(self):
        request = urllib2.Request('http://dl.bukkit.org/api/1.0/downloads/projects/craftbukkit/artifacts/dev/?_accept=application%2Fjson')
        buildList = json.loads(urllib2.urlopen(request).read())
        return buildList
class pluginSetupGui(QtGui.QDialog):
    def __init__(self, supported, pluginUrl):
        super(pluginSetupGui, self).__init__()
        if not supported:
            self.initUI(pluginUrl)
        elif supported and pluginUrl == 'Essentials':
            self.essentialsSetup()
    def initUI(self, pluginUrl):
        print pluginUrl
        self.pluginInformation = getPlugin().getGenericBukkitDevPluginInfo(str(pluginUrl))
        print self.pluginInformation
        self.pickVersionComboBox = QtGui.QComboBox()
        for version in self.pluginInformation['versions']['title']:
            self.pickVersionComboBox.addItem(version)
            print version

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
        self.downloadInformation = getPlugin().getGenericBukkitDevPluginDownloadInformation(self.pluginInformation['versions']['link'][self.pickVersionComboBox.currentIndex()])
        self.downloadUrlLabel.setText('URL: ' + self.downloadInformation['download'])
        self.md5HashLabel.setText('MD5: ' + self.downloadInformation['MD5'])
        self.supportedCB.setText('CB: ' + ", ".join(self.downloadInformation['supportedCraftBukkit']))
        #self.supportedCB.setText('CB: '+ str(self.downloadInformation['supportedCraftBukkit']))
        self.dialog = Downloader(self.downloadInformation['download'], targetDirectory + '/plugins/')
        self.dialog.exec_()
        if self.downloadInformation['download'].lower().endswith('.zip'):
            zipFileName = targetDirectory + "/plugins/" + self.downloadInformation['download'].split("/")[-1] # this will break if there are parameters on the URL but normally there aren't so it is safe
            try:
                zipExtraction = ZipFile(zipFileName)
                print zipFileName
                ZipFile.extractall(zipExtraction, targetDirectory + '/plugins/')
                ZipFile.close(zipExtraction)
                os.remove(zipFileName)
                self.completedSetupLabel = QLabel("Plugin setup complete.")
                self.completedSetupLabel.setStyleSheet('QLabel {color: green}')
                self.grid.addWidget(self.completedSetupLabel,7,1)
            except zipfile.BadZipFile, e:
                QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), 'ZIP file is corrupt.\r\nZipFile said: ' + e.message)
                self.completedSetupLabel = QLabel("Plugin setup failed.")
                self.completedSetupLabel.setStyleSheet('QLabel {color: red}')
                self.grid.addWidget(self.completedSetupLabel,7,1)

    def essentialsSetup(self):
        self.essentialsInformation = Essentials().getInfo('Release')
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
            QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), 'ZIP file is corrupted.\r\nZipFile said: ' + e.message)
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
        self.setWindowTitle('Qt Frame')
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
        else: # In most circumstances this should not be a problem.
            extension = 'sh'
        with open(targetDirectory + "/startserver." + extension, 'w') as script:
            script.write(scriptContents)
        if not os.name == "nt": # On Linux and a lot of other Unix-Likes you have to mark the file executable
            os.system('chmod +x ' + targetDirectory + "/startserver.sh")

class managerGui(QtGui.QDialog):
    def __init__(self):
        super(managerGui, self).__init__()
        self.initUI()
    def initUI(self):
        global targetDirectory
        targetDirectory = ''
        self.cacheBukkitRecommendedResultInfo = getServer().getRecommendedBukkitInfo()
        self.getBukkit = QtGui.QPushButton('Get Craftbukkit')
        self.bukkitEditions = QtGui.QComboBox(self)
        self.bukkitEditions.addItems(['Recommended', 'Beta', 'Development'])
        self.bukkitVersions = QtGui.QComboBox(self)
        self.bukkitVersionsLabel = QtGui.QLabel('Build: ' + str(self.cacheBukkitRecommendedResultInfo['results'][0]['build_number']))
        for result in self.cacheBukkitRecommendedResultInfo['results']:
            self.bukkitVersions.addItem(result['version'])
        self.setupStartupScriptButton = QtGui.QPushButton('Create Startup Script')


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
        bukkitGridLayout = QtGui.QVBoxLayout()
        bukkitGridLayout.setSpacing(10)
        bukkitGridLayout.addWidget(self.getBukkit,1)
        bukkitGridLayout.addWidget(self.bukkitEditions,2)
        bukkitGridLayout.addWidget(self.bukkitVersions,3)
        bukkitGridLayout.addWidget(self.bukkitVersionsLabel,4)
        bukkitGridLayout.addWidget(self.setupStartupScriptButton,5)

        pluginGrid = QtGui.QGroupBox("Plugin")
        pluginGridLayout = QtGui.QVBoxLayout()
        pluginGridLayout.setSpacing(10)
        pluginGridLayout.addWidget(self.pluginOfficialSupportComboBoxLabel,1)
        pluginGridLayout.addWidget(self.pluginOfficialSupportComboBox,2)
        pluginGridLayout.addWidget(self.installSupportedPluginButton,3)
        pluginGridLayout.addWidget(self.pluginCustomPluginUrlLabel,4)
        pluginGridLayout.addWidget(self.pluginCustomPluginUrl,5)
        pluginGridLayout.addWidget(self.installPluginButton,6)

        bukkitGrid.setLayout(bukkitGridLayout)
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

    def setupStartupScriptButtonClick(self):
        global targetDirectory
        if not targetDirectory == "":
            self.dialog = startupScriptSetup()
            self.dialog.exec_()
        else:
            QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), 'Please select a directory first.')
    def installSupportedPluginButtonPress(self):
        global targetDirectory
        if not targetDirectory == '':
            self.dialog = pluginSetupGui(True, self.pluginOfficialSupportComboBox.currentText())
            self.dialog.exec_()
        else:
            QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), 'Please select a directory first.')
    def installPluginButtonPress(self):
        global targetDirectory
        if not targetDirectory == '':
            self.dialog = pluginSetupGui(False, self.pluginCustomPluginUrl.text())
            self.dialog.exec_()
        else:
            QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), 'Please select a directory first.')
    def getBukkitButtonPress(self):
        global targetDirectory
        print targetDirectory
        if not targetDirectory == '':
            targetDirectory = targetDirectory + '/'
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
            QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), 'Please select a directory first.')
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
            QMessageBox.information(self, 'Error',
                                    'Unable to save the file %s: %s.' % (fileName, self.outFile.errorString()))
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
            QMessageBox.information(self, 'Error',
                                    'Download failed: %s.' % self.http.errorString())

        self.statusLabel.setText('Done')

    def readResponseHeader(self, responseHeader):
        # Check for genuine error conditions.
        if responseHeader.statusCode() not in (200, 300, 301, 302, 303, 307):
            QMessageBox.information(self, 'Error',
                                    'Download failed: %s.' % responseHeader.reasonPhrase())
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

# With thanks to Dinnerbone for this!
class MinecraftQuery:
    MAGIC_PREFIX = '\xFE\xFD'
    PACKET_TYPE_CHALLENGE = 9
    PACKET_TYPE_QUERY = 0
    HUMAN_READABLE_NAMES = dict(
        game_id     = "Game Name",
        gametype    = "Game Type",
        motd        = "Message of the Day",
        hostname    = "Server Address",
        hostport    = "Server Port",
        map         = "Main World Name",
        maxplayers  = "Maximum Players",
        numplayers  = "Players Online",
        players     = "List of Players",
        plugins     = "List of Plugins",
        raw_plugins = "Raw Plugin Info",
        software    = "Server Software",
        version     = "Game Version",
        )

    def __init__(self, host, port, timeout=10, id=0, retries=2):
        # Fixing port before it gets this far as will crash due to QString
        port = int(port)
        self.addr = (host, port)
        self.id = id
        self.id_packed = struct.pack('>l', id)
        self.challenge_packed = struct.pack('>l', 0)
        self.retries = 0
        self.max_retries = retries

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)

    def send_raw(self, data):
        self.socket.sendto(self.MAGIC_PREFIX + data, self.addr)

    def send_packet(self, type, data=''):
        self.send_raw(struct.pack('>B', type) + self.id_packed + self.challenge_packed + data)

    def read_packet(self):
        # This buffer is normally enough but I've encountered some huge servers which exceed this limit so I'll raise it
        # original is 1460
        buff = self.socket.recvfrom(99999)[0]
        type = struct.unpack('>B', buff[0])[0]
        id = struct.unpack('>l', buff[1:5])[0]
        return type, id, buff[5:]

    def handshake(self, bypass_retries=False):
        self.send_packet(self.PACKET_TYPE_CHALLENGE)

        try:
            type, id, buff = self.read_packet()
        except:
            if not bypass_retries:
                self.retries += 1

            if self.retries < self.max_retries:
                self.handshake(bypass_retries=bypass_retries)
                return
            else:
                raise

        self.challenge = int(buff[:-1])
        self.challenge_packed = struct.pack('>l', self.challenge)

    def get_status(self):
        if not hasattr(self, 'challenge'):
            self.handshake()

        self.send_packet(self.PACKET_TYPE_QUERY)

        try:
            type, id, buff = self.read_packet()
        except:
            self.handshake()
            return self.get_status()

        data = {}

        data['motd'], data['gametype'], data['map'], data['numplayers'], data['maxplayers'], buff = buff.split('\x00', 5)
        data['hostport'] = struct.unpack('<h', buff[:2])[0]
        buff = buff[2:]
        data['hostname'] = buff[:-1]

        for key in ('numplayers', 'maxplayers'):
            try:
                data[key] = int(data[key])
            except:
                pass

        return data

    def get_rules(self):
        if not hasattr(self, 'challenge'):
            self.handshake()

        self.send_packet(self.PACKET_TYPE_QUERY, self.id_packed)

        try:
            type, id, buff = self.read_packet()
        except:
            self.retries += 1
            if self.retries < self.max_retries:
                self.handshake(bypass_retries=True)
                return self.get_rules()
            else:
                raise

        data = {}

        buff = buff[11:] # splitnum + 2 ints
        items, players = buff.split('\x00\x00\x01player_\x00\x00') # Shamefully stole from https://github.com/barneygale/MCQuery

        if items[:8] == 'hostname':
            items = 'motd' + items[8:]

        items = items.split('\x00')
        data = dict(zip(items[::2], items[1::2]))

        players = players[:-2]

        if players:
            data['players'] = players.split('\x00')
        else:
            data['players'] = []

        for key in ('numplayers', 'maxplayers', 'hostport'):
            try:
                data[key] = int(data[key])
            except:
                pass

        data['raw_plugins'] = data['plugins']
        data['software'], data['plugins'] = self.parse_plugins(data['raw_plugins'])

        return data

    def parse_plugins(self, raw):
        parts = raw.split(':', 1)
        server = parts[0].strip()
        plugins = []

        if len(parts) == 2:
            plugins = parts[1].split(';')
            plugins = map(lambda s: s.strip(), plugins)

        return server, plugins


main()

