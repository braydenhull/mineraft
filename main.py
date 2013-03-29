__author__ = 'brayden'
import urllib2
import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMessageBox, QFileDialog
import os
from minecraftQuery import MinecraftQuery
from server import getServer
from downloadWidget import Downloader
from pluginSetupWidget import pluginSetupGui
from essentialsSetupWidget import essentialsSetupGui
from startupScriptWidget import startupScriptSetup
from configureServerPropertiesWidget import configureServerProperties
import socket

nativePluginSupport = ['Essentials']

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
        self.configureServerPropertiesButton = QtGui.QPushButton('Configure')

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
        self.statusIpAddress.setFixedWidth(100)
        self.statusIpAddressLabel = QtGui.QLabel('IP: ')
        self.statusPortNumber = QtGui.QLineEdit('25565')
        self.statusPortNumber.setFixedWidth(40)
        self.statusPortNumber.setMaxLength(5)
        self.statusPortNumberLabel = QtGui.QLabel('Port: ')
        self.statusRefreshButton = QtGui.QPushButton('Refresh')
        self.statusConnectedPlayers = QtGui.QListWidget()
        self.statusConnectedPlayers.setMaximumWidth(125)
        self.statusConnectedPlayersLabel = QtGui.QLabel('Connected Players')
        self.statusInstalledPlugins = QtGui.QListWidget()
        self.statusInstalledPluginsLabel = QtGui.QLabel('Installed Plugins')
        self.statusMinecraftVersion = QtGui.QLabel('Version: ')
        self.statusMaxPlayers = QtGui.QLabel('Max Players: ')
        self.statusTimeoutLabel = QtGui.QLabel('Timeout: ')
        self.statusTimeout = QtGui.QLineEdit(str(3))
        self.statusTimeout.setFixedWidth(40)
        self.statusTimeout.setMaxLength(3)

        bukkitGrid = QtGui.QGroupBox("Bukkit")
        self.bukkitGridLayout = QtGui.QVBoxLayout()
        self.bukkitGridLayout.setSpacing(10)
        self.bukkitGridLayout.addWidget(self.getBukkit,1)
        self.bukkitGridLayout.addWidget(self.bukkitEditions,2)
        self.bukkitGridLayout.addWidget(self.bukkitVersions,3)
        self.bukkitGridLayout.addWidget(self.bukkitVersionsLabel,4)
        self.bukkitGridLayout.addWidget(self.setupStartupScriptButton,5)
        self.bukkitGridLayout.addWidget(self.configureServerPropertiesButton,6)
        self.bukkitGridLayout.addWidget(self.startServer,7)

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
        self.grid.addWidget(self.statusIpAddressLabel,3,0,QtCore.Qt.AlignLeft)
        self.grid.addWidget(self.statusIpAddress,3,0,QtCore.Qt.AlignRight)
        self.grid.addWidget(self.statusPortNumberLabel,3,1,QtCore.Qt.AlignLeft)
        self.grid.addWidget(self.statusPortNumber,3,1,QtCore.Qt.AlignRight)
        self.grid.addWidget(self.statusTimeoutLabel,5,0,QtCore.Qt.AlignLeft)
        self.grid.addWidget(self.statusTimeout,5,0,QtCore.Qt.AlignRight)
        self.grid.addWidget(self.statusConnectedPlayersLabel,6,0)
        self.grid.addWidget(self.statusConnectedPlayers,7,0)
        self.grid.addWidget(self.statusInstalledPluginsLabel,6,1)
        self.grid.addWidget(self.statusInstalledPlugins,7,1)
        self.grid.addWidget(self.statusMaxPlayers,8,0)
        self.grid.addWidget(self.statusMinecraftVersion,8,1)
        self.grid.addWidget(self.statusRefreshButton,5,1)

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
        self.configureServerPropertiesButton.clicked.connect(self.configureServerPropertiesButtonClicked)

    def configureServerPropertiesButtonClicked(self):
        global targetDirectory
        if not targetDirectory == "":
            self.dialog = configureServerProperties(targetDirectory)
            self.dialog.exec_()
        else:
            QtGui.QMessageBox.critical(self, 'Error', 'Please select a directory first.')
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
                os.system('open ' + targetDirectory + '/startserver' + extension + '&') # I haven't tested if & is necessary but I'll assume it is
            else:
                os.system('xterm ' + targetDirectory + '/startserver' + extension + '&')
        else:
            #QtGui.QErrorMessage.showMessage(QtGui.QErrorMessage.qtHandler(), 'Please select a directory first.')
            QtGui.QMessageBox.critical(self, 'Error', 'Please select a directory first.')
    def setupStartupScriptButtonClick(self):
        global targetDirectory
        if not targetDirectory == "":
            self.dialog = startupScriptSetup(targetDirectory)
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
            #self.dialog = pluginSetupGui(True, self.pluginOfficialSupportComboBox.currentText(), targetDirectory)
            if self.pluginOfficialSupportComboBox.currentText() == 'Essentials':
                self.dialog = essentialsSetupGui(targetDirectory)
            self.dialog.exec_()
        else:
            QtGui.QMessageBox.critical(self, 'Error', 'Please select a directory first.')
    def installPluginButtonPress(self):
        global targetDirectory
        if not targetDirectory == '':
            self.dialog = pluginSetupGui(False, self.pluginCustomPluginUrl.text(), targetDirectory)
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
        try:
            self.minecraftQueryInformation = self.minecraftQuery.get_rules()
        except socket.error, e:
            QtGui.QMessageBox.critical(self, 'Error', 'Socket Error.\r\nIs the server running on that port/IP?\r\nIs enable-query set to true in server.properties?\r\n' + e.message)
        self.statusMaxPlayers.setText('Max Players: ' + str(self.minecraftQueryInformation['maxplayers']))
        self.statusMinecraftVersion.setText('Version: ' + self.minecraftQueryInformation['version'])
        # If you forget to clear the list then all the items double up
        self.statusInstalledPlugins.clear()
        self.statusInstalledPlugins.addItems(self.minecraftQueryInformation['plugins'])
        self.statusConnectedPlayers.clear()
        self.statusConnectedPlayers.addItems(self.minecraftQueryInformation['players'])


def main():
    app = QtGui.QApplication(sys.argv)
    ex = managerGui()
    sys.exit(app.exec_())

main()