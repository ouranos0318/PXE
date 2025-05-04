from PyQt5.QtWidgets import QWidget,QApplication,QFileDialog
from PyQt5.QtCore import Qt, QObject
from qfluentwidgets import FluentIcon as FIF

from UI.Ui_AUTO import Ui_AUTO

class AutoPage(QWidget, Ui_AUTO):
    """ test interface """
    res_dict = {}
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.PrimaryToolButton_Import.setIcon(FIF.FOLDER)
        self.PrimaryToolButton_Import.clicked.connect(self.selectFile)
        self.CheckBox_Cfg.toggled.connect(self.onCheckedChanged)
        self.TextEdit_Custom.hide()  # 初始时隐藏TextEdit_Custom
        # 自定义分区按钮
        self.CheckBox_Custom.toggled.connect(lambda: self.TextEdit_Custom.setVisible(self.CheckBox_Custom.isChecked()))


    def onCheckedChanged(self):
        status = self.CheckBox_Cfg.isChecked()
        disable_list = [
            self.CheckBox_Encrypty,     # 开启加密
            self.CheckBox_Lvm,          # LVM逻辑卷按照
            self.LineEdit_EncryptyPWD,  # 加密密钥
            self.CheckBox_Autologin,    # 自动登录
            self.CheckBox_Oobe,         # OOBE流程
            self.CheckBox_Reboot,       # 安装后重启
            self.CheckBox_swapfile,     # SwapFile
            self.CheckBox_unformat,     # 保留用户数据
            self.CheckBox_Backup,       # 出厂备份
            self.CheckBox_Automatic,    # 自动安装
            self.LineEdit_HostName,     # 主机名
            self.LineEdit_Devpath,      # 全盘安装路径
            self.LineEdit_UserName,     # 用户名
            self.LineEdit_UserPWD,      # 密码
            self.LineEdit_Timezone,     # 时区
            self.CheckBox_Custom,       # 自定义分区
        ]
        for disable in disable_list:
            disable.setDisabled(status)

    def init_dict(self):
        self.res_dict['IMPORT'] = self.CheckBox_Cfg.isChecked()
        self.res_dict['IMPORT_PATH'] = self.LineEdit_Import.text()
        self.res_dict['ENCRYPTY'] = self.CheckBox_Encrypty.isChecked()
        self.res_dict['LVM'] = self.CheckBox_Lvm.isChecked()
        self.res_dict['ENCRYPTY_PWD'] = self.LineEdit_EncryptyPWD.text()

    def selectFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择文件', '', '文本文件 (*.iso);;所有文件 (*)')
        if file_path:
            self.LineEdit_Import.setText(file_path)

    def get_dict(self):
        return {}