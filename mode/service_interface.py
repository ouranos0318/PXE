import sys, os, pwd
sys.path.append(r'../UI')

from PyQt5.QtWidgets import QWidget,QFileDialog
from qfluentwidgets import FluentIcon as FIF

from UI.Ui_SERVICE import Ui_SERVICE

class ServicePage(QWidget, Ui_SERVICE):
    """ test interface """
    res_dict = {}
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        # 在线安装时不显示组件路径
        self.LineEdit_ComponentsPath.setVisible(False)
        self.PrimaryToolButton_ComponentsPath.setVisible(False)
        self.SwitchButton_Components.checkedChanged.connect(self.onCheckedChanged)
        # 设置按钮图标
        self.PrimaryToolButton_CheckISO.setIcon(FIF.FOLDER)
        self.PrimaryToolButton_ComponentsPath.setIcon(FIF.FOLDER)
        # 获取ISO文件路径
        self.PrimaryToolButton_CheckISO.clicked.connect(self.selectFile)
        # 获取组件路径
        self.PrimaryToolButton_ComponentsPath.clicked.connect(self.selectFolder)

    def get_selected_radio_text(self, *raodo):
        """
        获取指定按钮组中被选中的RadioButton的文本
        :param button_group: QButtonGroup对象
        :return: 被选中的RadioButton的文本，如果没有选中则返回空字符串
        """
        for button in raodo:
            if button.isChecked():
                return button.text()
        return ""

    # 离线安装时显示组件路径
    def onCheckedChanged(self, isChecked: bool):
        status = False if isChecked else True
        self.LineEdit_ComponentsPath.setVisible(status)
        self.PrimaryToolButton_ComponentsPath.setVisible(status)

    def get_user_home(self):
        """ 获取原始用户的家目录（处理 sudo 场景） """
        try:
            # sudo 运行时，SUDO_USER 保存原始用户名（如 chris）
            username = os.environ.get('SUDO_USER', os.getlogin())
            # 通过用户名获取家目录
            return pwd.getpwnam(username).pw_dir
        except Exception as e:
            print(f"获取用户家目录失败: {e}")
            return os.path.expanduser("~")  # 回退到当前用户家目录（可能是 root）

    def selectFile(self):
        # 使用原始用户的家目录作为初始路径
        home_dir = self.get_user_home()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择文件',
            f'{home_dir}/桌面/',  # 初始路径改为原始用户家目录
            'ISO 文件 (*.iso);;所有文件 (*)'  # 修正：明确筛选 ISO 文件
        )
        if file_path:
            self.LineEdit_ISOPath.setText(file_path)

    def selectFolder(self):
        # 使用原始用户的家目录作为初始路径
        home_dir = self.get_user_home()
        folder_path = QFileDialog.getExistingDirectory(
            self,
            '选择文件夹',
            home_dir  # 初始路径改为原始用户家目录
        )
        if folder_path:
            self.LineEdit_ComponentsPath.setText(folder_path)

    def get_dict(self):
       self.res_dict['ISO_PATH'] = self.LineEdit_ISOPath.text()
       self.res_dict['COMPONENTS_PATH'] = self.LineEdit_ComponentsPath.text()
       self.res_dict['MODE'] = self.get_selected_radio_text(self.RadioButton_ISOMode, self.RadioButton_FileMode)
       self.res_dict['ARCH'] = self.get_selected_radio_text(self.RadioButton_ARM, self.RadioButton_X86)
       self.res_dict['ONLINE_INSTALL'] = self.SwitchButton_Components.isChecked()
       return self.res_dict

