from PyQt5.QtWidgets import QWidget,QApplication,QFileDialog
from PyQt5.QtCore import Qt,QCoreApplication
from qfluentwidgets import FluentIcon as FIF
from UI.Ui_DEPLOY import Ui_DEPLOY
from PyQt5.QtGui import QTextCharFormat, QColor
import time
import subprocess
import psutil

class DeployPage(QWidget, Ui_DEPLOY):
    res_dict = {}
    """ test interface """


    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.initPrimaryToolButton()
        self.start_service_check()

    def initPrimaryToolButton(self):
        self.PrimaryToolButton_DHCP.setDisabled(True)
        self.PrimaryToolButton_TFTP.setDisabled(True)
        self.PrimaryToolButton_NFS.setDisabled(True)
        self.PrimaryToolButton_HTTPD.setDisabled(True)

    def get_dict(self):
        return self.res_dict

    def add_content_to_textedit(self, text, color=None):
        cursor = self.PlainTextEdit.textCursor()
        if color:
            format = QTextCharFormat()
            format.setForeground(color)
            cursor.setCharFormat(format)
        cursor.insertText(text + '\n')
        self.PlainTextEdit.setTextCursor(cursor)
        
    def check_services_status(self):
        services = ['dhcpd', 'tftpd', 'nfs-server', 'httpd']
        for service in services:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                is_running = result.stdout.strip() == 'active'
            except Exception as e:
                # TODO 打开日志
                # self.add_content_to_textedit(f"检查服务 {service} 状态时出错: {e}", QColor('red'))
                is_running = False
            if service == 'dhcpd':
                self.PrimaryToolButton_DHCP.setDisabled(not is_running)
            elif service == 'tftpd':
                self.PrimaryToolButton_TFTP.setDisabled(not is_running)
            elif service == 'nfs-server':
                self.PrimaryToolButton_NFS.setDisabled(not is_running)
            elif service == 'httpd':
                self.PrimaryToolButton_HTTPD.setDisabled(not is_running)

    def start_service_check(self):
        from PyQt5.QtCore import QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_services_status)
        self.timer.start(5000)  # 每5秒检查一次