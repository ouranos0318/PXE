import sys
sys.path.append(r'../UI')

from PyQt5.QtWidgets import QWidget,QFileDialog
from qfluentwidgets import FluentIcon as FIF

from UI.Ui_SERVICE import Ui_SERVICE

class ServicePage(QWidget, Ui_SERVICE):
    """ test interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.res_dict = {}
        self.init_dict()

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

    def init_dict(self):
        self.res_dict['ISO_PATH'] = ''
        self.res_dict['MODE'] = self.get_selected_radio_text(self.RadioButton_ISOMode, self.RadioButton_FileMode)
        self.res_dict['ARCH'] = self.get_selected_radio_text(self.RadioButton_ARM, self.RadioButton_X86)
        self.res_dict['ONLINE_INSTALL'] = self.SwitchButton_Components.isChecked()


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


    def selectFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择文件', '', '文本文件 (*.iso);;所有文件 (*)')
        if file_path:
            self.LineEdit_ISOPath.setText(file_path)

    def selectFolder(self):
        folder_path = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if folder_path:
            self.LineEdit_ComponentsPath.setText(folder_path)

    def get_dict(self):
       self.res_dict['ISO_PATH'] = self.LineEdit_ISOPath.text()
       self.res_dict['COMPONENTS_PATH'] = self.LineEdit_ComponentsPath.text()
       self.res_dict['MODE'] = self.get_selected_radio_text(self.RadioButton_ISOMode, self.RadioButton_FileMode)
       self.res_dict['ARCH'] = self.get_selected_radio_text(self.RadioButton_ARM, self.RadioButton_X86)
       self.res_dict['ONLINE_INSTALL'] = self.SwitchButton_Components.isChecked()
       return self.res_dict

