from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QCoreApplication,QTimer
from UI.Ui_DEPLOY import Ui_DEPLOY
from PyQt5.QtGui import QTextCharFormat, QColor
import subprocess


class DeployPage(QWidget, Ui_DEPLOY):
    res_dict = {}
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

    def add_content_to_textedit(self, text, color=None, font_size=10):
        cursor = self.PlainTextEdit.textCursor()
        _format = QTextCharFormat()
        if color:
            _format.setForeground(color)
        _format.setFontPointSize(font_size)
        cursor.setCharFormat(_format)
        cursor.insertText(text + '\n')
        self.PlainTextEdit.setTextCursor(cursor)
        QCoreApplication.processEvents()

    def check_services_status(self):
        # 修正 dhcp 服务名称
        services = ['isc-dhcp-server', 'tftpd-hpa', 'nfs-server', 'httpd']
        button_mapping = {
            'isc-dhcp-server': self.PrimaryToolButton_DHCP,
            'tftpd-hpa': self.PrimaryToolButton_TFTP,
            'nfs-server': self.PrimaryToolButton_NFS,
            'httpd': self.PrimaryToolButton_HTTPD
        }
        for service in services:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
                is_running = result.stdout.strip() == 'active'
                # print(f"服务 {service} 状态: {'active' if is_running else 'inactive'}")  # 添加日志输出
            except Exception as e:
                # self.add_content_to_textedit(f"检查服务 {service} 状态时出错: {e}", QColor('red'))
                is_running = False
            button = button_mapping.get(service)
            if button:
                button.setDisabled(not is_running)
                # print(f"服务 {service} 对应按钮状态已更新为 {'启用' if not is_running else '禁用'}")  # 添加日志输出




    def start_service_check(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_services_status)
        self.timer.start(5000)  # 每5秒检查一次