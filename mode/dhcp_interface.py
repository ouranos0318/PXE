import psutil
import socket
from PyQt5.QtWidgets import QWidget
from UI.Ui_DHCP import Ui_DHCP


def get_net_interface():
    interfaces = psutil.net_if_addrs().keys()
    return [iface for iface in interfaces if iface != "lo"]


def get_ip_by_interface(interface_name):
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


class DHCPPage(QWidget, Ui_DHCP):
    res_dict = {}
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.ComboBox_NetName.setPlaceholderText('选择网卡')
        self.ComboBox_NetName.setCurrentIndex(-1)
        self.ComboBox_NetName.addItems(get_net_interface())
        self.ComboBox_NetName.currentIndexChanged.connect(self.ComboBox_NetName_currentIndexChanged)
        
    # def get_dict(self):
    #     self.res_dict['START_IP'] = self.LineEdit_StartSubNet.text()
    #     self.res_dict['END_IP'] = self.LineEdit_EndSubNet.text()
    #     self.res_dict['NET_INTER_NAME'] = self.ComboBox_NetName.currentText()
    #     self.res_dict['NET_INTER_IP'] = get_ip_by_interface(self.res_dict['NET_INTER_NAME'])
    #     return self.res_dict

    def ComboBox_NetName_currentIndexChanged(self, index):
        if index == -1:
            print('-1 索引不允许被选择')
            return
        print(f'{index}:引用了on_ComboBox_NetName_currentIndexChanged')
        selected_text = self.ComboBox_NetName.itemText(index)
        network_segment = '.'.join(get_ip_by_interface(selected_text).split('.')[:3])
        self.LineEdit_StartSubNet.setText(f'{network_segment}.200')
        self.LineEdit_EndSubNet.setText(f'{network_segment}.210')