__author__ = 'brayden'

from PyQt4.QtGui import QApplication, QDialog, QProgressBar, QLabel, QPushButton, QDialogButtonBox, \
    QVBoxLayout, QMessageBox, QFileDialog
from PyQt4.QtNetwork import QHttp
from urlparse import urlparse
from PyQt4.QtCore import QUrl, QFileInfo, QFile, QIODevice


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