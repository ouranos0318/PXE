import psutil
import socket
from PyQt5.QtWidgets import QWidget,QApplication
from PyQt5.QtCore import Qt
from qfluentwidgets import FluentIcon as FIF
from UI.Ui_DHCP import Ui_DHCP




class DHCPPage(QWidget, Ui_DHCP):
    """ test interface """
    
    res_dict = {}
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.init_dict()
        self.NetNames = self.get_net_interface()
        self.ComboBox_NetName.addItems(self.NetNames)
        self.ComboBox_NetName.setPlaceholderText('选择网卡')
        self.ComboBox_NetName.setCurrentIndex(-1)

    def init_dict(self):
        # 设置默认IP地址
        self.LineEdit_StartSubNet.setText('192.168.100.200')
        self.LineEdit_EndSubNet.setText('192.168.100.210')
        # 初始化字典
        self.res_dict['NET_INTER_NAME'] = ''
        self.res_dict['START_IP'] = self.LineEdit_StartSubNet.text()
        self.res_dict['END_IP'] = self.LineEdit_EndSubNet.text()

    def get_dict(self):
        self.res_dict['START_IP'] = self.LineEdit_StartSubNet.text()
        self.res_dict['END_IP'] = self.LineEdit_EndSubNet.text()
        self.res_dict['NET_INTER_NAME'] = self.ComboBox_NetName.currentText()
        self.res_dict['NET_INTER_IP'] = self.get_ip_by_interface(self.res_dict['NET_INTER_NAME'])
        return self.res_dict

    def get_net_interface(self):
        interfaces = psutil.net_if_addrs().keys()
        return [iface for iface in interfaces if iface != "lo"]

    def get_ip_by_interface(self,interface_name):
        """
        通过网卡名获取 IP 地址
        :param interface_name: 网卡名称
        :return: 网卡对应的 IP 地址，如果未找到则返回空字符串
        """
        addrs = psutil.net_if_addrs()
        if interface_name in addrs:
            for addr in addrs[interface_name]:
                if addr.family == socket.AF_INET:
                    return addr.address
        return ""