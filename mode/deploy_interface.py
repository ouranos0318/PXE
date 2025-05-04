from PyQt5.QtWidgets import QWidget,QApplication,QFileDialog
from PyQt5.QtCore import Qt,QCoreApplication
from qfluentwidgets import FluentIcon as FIF
from UI.Ui_DEPLOY import Ui_DEPLOY
import time

class DeployPage(QWidget, Ui_DEPLOY):
    res_dict = {}
    """ test interface """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.initPrimaryToolButton()

    def initPrimaryToolButton(self):
        self.PrimaryToolButton_DHCP.setDisabled(True)
        self.PrimaryToolButton_TFTP.setDisabled(True)
        self.PrimaryToolButton_NFS.setDisabled(True)
        self.PrimaryToolButton_HTTPD.setDisabled(True)

    def get_dict(self):
        return {}

    def add_content_to_textedit(self,text):
        self.PlainTextEdit.appendPlainText(text)



