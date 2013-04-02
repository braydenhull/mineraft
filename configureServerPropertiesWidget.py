__author__ = 'brayden'

from PyQt4 import QtGui
from PyQt4 import QtCore
import os

class configureServerProperties(QtGui.QDialog):
    def __init__(self, targetDirectory):
        super(configureServerProperties, self).__init__()
        self.targetDirectory = targetDirectory
        self.initUI()
    def initUI(self):
        self.serverport = QtGui.QSpinBox()
        self.serverport.setRange(0, 65535)
        self.serverport.setValue(25565)
        self.serverport.setMaximumWidth(55)
        self.serverportLabel = QtGui.QLabel('Server Port')

        self.motd = QtGui.QLineEdit('A Minecraft server')
        self.motdLabel = QtGui.QLabel('MOTD')
        self.motdLabel.setToolTip('Message of the Day')

        self.enableQuery = QtGui.QCheckBox()
        self.enableQuery.setChecked(True)
        self.enableQueryLabel = QtGui.QLabel('Enable Query')

        self.pvp = QtGui.QCheckBox()
        self.pvp.setChecked(True)
        self.pvpLabel = QtGui.QLabel('PVP')
        self.pvpLabel.setToolTip('Player versus Player<br>Whether players can injure each other.')

        self.rcon = QtGui.QCheckBox()
        self.rcon.setChecked(False)
        self.rconLabel = QtGui.QLabel('Rcon')
        self.rconLabel.setToolTip('Remote Console<br>Do not enable unless you need it.')

        self.gamemode = QtGui.QComboBox()
        self.gamemode.addItems(['Survival', 'Creative', 'Adventure'])
        self.gamemode.setMaximumWidth(75)
        self.gamemodeLabel = QtGui.QLabel('Gamemode')

        self.onlineMode = QtGui.QCheckBox()
        self.onlineMode.setChecked(True)
        self.onlineModeLabel = QtGui.QLabel('Online Mode')
        self.onlineModeLabel.setToolTip('Disable if Mojang login servers are down or if your account is not premium.')

        self.whitelistButton = QtGui.QPushButton('Whitelist')
        self.whitelistCheckBox = QtGui.QCheckBox()
        self.whitelistCheckBox.setChecked(False)
        self.whiteListLabel = QtGui.QLabel('Whitelist')
        self.saveAndQuitButton = QtGui.QPushButton('Save') # It won't print ampersands unless you write them twice

        self.maxplayers = QtGui.QSpinBox()
        self.maxplayers.setValue(20)
        self.maxplayers.setRange(0,999)
        self.maxplayers.setMaximumWidth(40)
        self.maxplayersLabel = QtGui.QLabel('Max Players')

        self.configureOps = QtGui.QPushButton('Server Operators')

        grid = QtGui.QGridLayout()
        grid.addWidget(self.serverport,1,1)
        grid.addWidget(self.serverportLabel,1,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.motd,2,1)
        grid.addWidget(self.motdLabel,2,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.enableQuery,3,1)
        grid.addWidget(self.enableQueryLabel,3,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.pvp,4,1)
        grid.addWidget(self.pvpLabel,4,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.rcon,5,1)
        grid.addWidget(self.rconLabel,5,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.gamemode,6,1)
        grid.addWidget(self.gamemodeLabel,6,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.onlineMode,7,1)
        grid.addWidget(self.onlineModeLabel,7,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.whitelistCheckBox,8,1)
        grid.addWidget(self.whiteListLabel,8,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.maxplayers,9,1)
        grid.addWidget(self.maxplayersLabel,9,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.whitelistButton,10,0)
        grid.addWidget(self.configureOps,10,1)
        grid.addWidget(self.saveAndQuitButton,11,0)

        self.setLayout(grid)
        self.setWindowTitle('Server.properties Configuration')
        self.show()
        self.whitelistButton.clicked.connect(self.openWhitelist)
        self.saveAndQuitButton.clicked.connect(self.saveAndQuit)
        self.configureOps.clicked.connect(self.openOpsSetup)
    def openOpsSetup(self):
        self.dialog = opsSetup(self.targetDirectory)
        self.dialog.exec_()
    def openWhitelist(self):
        self.dialog = whitelistSetup(self.targetDirectory)
        self.dialog.exec_()
    def saveAndQuit(self):
        propertiesFileContents = ["#Minecraft server properties",
        "generator-settings=",
        "allow-nether=true",
        "level-name=world",
        "enable-query=true" if self.enableQuery.isChecked() else "enable-query=false",
        "allow-flight=false",
        "server-port=" + self.serverport.text(),
        "query.port=" + self.serverport.text(),
        "level-type=DEFAULT",
        "enable-rcon=true" if self.rcon.isChecked() else "enable-rcon=false",
        "level-seed=",
        "server-ip=",
        "max-build-height=256",
        "spawn-npcs=true",
        "debug=false",
        "white-list=true" if self.whitelistCheckBox.isChecked() else "white-list=false",
        "spawn-animals=true",
        "snooper-enabled=true",
        "hardcore=false",
        "texture-pack=",
        "online-mode=true",
        "pvp=true" if self.pvp.isChecked() else "pvp=false",
        "difficulty=1",
        "gamemode=" + str(self.gamemode.currentIndex()),
        "max-players=" + self.maxplayers.text(),
        "spawn-monsters=true",
        "view-distance=10",
        "generate-structures=true",
        "spawn-protection=16",
        "motd=" + self.motd.text()]
        f = open(self.targetDirectory + '/server.properties', 'w')
        for s in propertiesFileContents:
            f.write("%s\n" % s)
        f.close()
        #self.close()

class whitelistSetup(QtGui.QDialog):
    def __init__(self, targetDirectory):
        super(whitelistSetup, self).__init__()
        self.targetDirectory = targetDirectory
        self.initUI()
    def initUI(self):
        self.userList = QtGui.QListWidget()
        if not os.path.exists(self.targetDirectory + '/white-list.txt'):
            open(self.targetDirectory + '/white-list.txt', 'w').close()
        f = open(self.targetDirectory + '/white-list.txt' ,'r')
        for s in f.readlines():
            print s
            self.userList.addItem(s.strip())
        f.close()
        self.addUser = QtGui.QPushButton('Add')
        self.userField = QtGui.QLineEdit()
        self.userField.setMaxLength(16)
        self.userField.setFixedWidth(105)
        self.information = QtGui.QLabel('Whitelisted Users\r\nInsert username and press add')
        self.deleteUser = QtGui.QPushButton('Delete')
        self.saveAndClose = QtGui.QPushButton('Save && Close') # To display the ampersand there needs to be 2 of them!

        grid = QtGui.QGridLayout()
        grid.addWidget(self.information,0,0)
        grid.addWidget(self.userList,1,0)
        grid.addWidget(self.userField,2,0,QtCore.Qt.AlignLeft)
        grid.addWidget(self.addUser,2,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.deleteUser,3,0,QtCore.Qt.AlignLeft)
        grid.addWidget(self.saveAndClose,3,0,QtCore.Qt.AlignRight)

        self.setLayout(grid)
        self.setWindowTitle('Whitelist Configuration')
        self.show()
        self.addUser.clicked.connect(self.addUserToList)
        self.deleteUser.clicked.connect(self.deleteUserFromList)
        self.saveAndClose.clicked.connect(self.saveWhitelist)
    def addUserToList(self):
        self.userList.addItem(self.userField.text())
        self.userField.clear()

    def deleteUserFromList(self):
        self.userList.takeItem(self.userList.currentRow()) # God damn takeItem? Terrible name :(

    def saveWhitelist(self):
        items = []
        for s in xrange(self.userList.count()):
            items.append(self.userList.item(s))
        labels = [i.text() for i in items]
        print labels
        print self.targetDirectory
        f = open(self.targetDirectory + '/white-list.txt', 'w')
        for item in labels:
            f.write("%s\n" % item)
        f.close()
        self.close()

class opsSetup(QtGui.QDialog):
    def __init__(self, targetDirectory):
        super(opsSetup, self).__init__()
        self.targetDirectory = targetDirectory
        self.initUI()
    def initUI(self):
        self.userList = QtGui.QListWidget()
        if not os.path.exists(self.targetDirectory + '/ops.txt'):
            open(self.targetDirectory + '/ops.txt', 'w').close()
        f = open(self.targetDirectory + '/ops.txt', 'r')
        for s in f.readlines():
            self.userList.addItem(s.strip())
        f.close()
        self.addUser = QtGui.QPushButton('Add')
        self.userField = QtGui.QLineEdit()
        self.userField.setMaxLength(16)
        self.userField.setFixedWidth(105)
        self.information = QtGui.QLabel('Operator Privileges\r\nInsert username and press Add')
        self.deleteUser = QtGui.QPushButton('Delete')
        self.saveAndClose = QtGui.QPushButton('Save && Close') # Needs && to print &

        grid = QtGui.QGridLayout()
        grid.addWidget(self.information,0,0)
        grid.addWidget(self.userList,1,0)
        grid.addWidget(self.userField,2,0,QtCore.Qt.AlignLeft)
        grid.addWidget(self.addUser,2,0,QtCore.Qt.AlignRight)
        grid.addWidget(self.deleteUser,3,0,QtCore.Qt.AlignLeft)
        grid.addWidget(self.saveAndClose,3,0,QtCore.Qt.AlignRight)
        self.addUser.clicked.connect(self.addUserToList)
        self.deleteUser.clicked.connect(self.deleteUserFromList)
        self.saveAndClose.clicked.connect(self.saveWhitelist)

        self.setLayout(grid)
        self.setWindowTitle('Ops Configuration')
        self.show()

    def addUserToList(self):
        self.userList.addItem(self.userField.text())
        self.userField.clear()

    def deleteUserFromList(self):
        self.userList.takeItem(self.userList.currentRow()) # God damn takeItem? Terrible name :(

    def saveWhitelist(self):
        items = []
        for s in xrange(self.userList.count()):
            items.append(self.userList.item(s))
        labels = [i.text() for i in items]
        print labels
        print self.targetDirectory
        f = open(self.targetDirectory + '/ops.txt', 'w')
        for item in labels:
            f.write("%s\n" % item)
        f.close()
        self.close()
