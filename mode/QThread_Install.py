import os
import subprocess
from configparser import ConfigParser
from PyQt5.QtCore import QThread, pyqtSignal

def shellcmd(cmd) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

# 检查ip是否在同一网段
def ipCheck(ip1, ip2):
    ip1_parts = ip1.split('.')
    ip2_parts = ip2.split('.')
    if len(ip1_parts) != 4 or len(ip2_parts) != 4:
        return False
    # 比较前三个网段
    for i in range(3):
        if ip1_parts[i] != ip2_parts[i]:
            return False
    return True

class _Logger:
    def __init__(self, fun):
        self.logobj = fun
    def info(self, text):
        self.logobj.emit(('info', text))
    def error(self, text):
        self.logobj.emit(('error', text))
    def warn(self, text):
        self.logobj.emit(('warn', text))
    def tip(self, text):
        self.logobj.emit(('tip', text))

class Installer(QThread):
    output_signal = pyqtSignal(tuple)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    def __init__(self, res_dict):
        super().__init__()
        self.running = False
        self.log = _Logger(self.output_signal)
        self.res_dict = res_dict
        self.config = ConfigParser()
        self.packages ='isc-dhcp-server nfs-kernel-server tftpd-hpa'
        self.mode = self.res_dict['MODE']
        self.iso_dir = ''


    def check_result_dict(self):
        modifier = '*' * 10
        flag = True
        # 检查service_interface配置项
        self.log.info(f"{modifier}检查基础页配置项{modifier}")
        if not self.res_dict['ISO_PATH']:
            self.log.error(f"ISO路径不能为空,进程停止")
            flag = False
        if not self.res_dict['ONLINE_INSTALL']:
            if not self.res_dict['COMPONENTS_PATH']:
                self.log.error(f"选择离线安装时,组件路径不能为空,进程停止")
                flag = False

        self.log.info(f"{modifier}检查DHCP配置项{modifier}")
        if self.res_dict['NET_INTER_IP'] and not self.res_dict['NET_INTER_IP'].startswith('169.254.'):
            if not ipCheck(self.res_dict['NET_INTER_IP'], self.res_dict['START_IP']):
                self.log.error(f"网络接口IP与起始IP不在同一网段,进程停止")
                flag = False
            if not ipCheck(self.res_dict['NET_INTER_IP'], self.res_dict['END_IP']):
                self.log.error(f"网络接口IP与结束IP不在同一网段,进程停止")
                flag = False
            if self.res_dict['START_IP'] > self.res_dict['END_IP']:
                self.log.error(f"起始IP:{self.res_dict['START_IP']}大于结束IP:{self.res_dict['END_IP']},进程停止",)
                flag = False

        else:
            self.log.error(f"网卡IP为空或为169.254.xxx.xxx,进程停止")
            flag = False
        # 检查auto_interface配置项
        self.log.info(f"{modifier}检查AUTO页配置项{modifier}")

        # 检查自定义全盘安装时 加密和LVM功能是否关闭
        if self.res_dict['CUSTOM'] and  ( self.res_dict['ENCRYPTY'] or self.res_dict['LVM'] or self.res_dict['UNFORMAT'] ):
            self.log.error(f"全盘安装不支持加密、LVM功能和保留用户数据功能,进程停止")
            flag = False

        return flag

    def install_package(self):
        flag = True
        self.log.info(f"开始安装软件包")
        # 安装组件包
        if self.res_dict['ONLINE_INSTALL']:
            # 在线安装
            try:
                self.log.info(f"开始在线安装组件包")
                install_packages = shellcmd(f'apt install -y {self.packages}')
                if install_packages.returncode:
                    self.log.error(f'在线安装组件包失败，错误信息：{install_packages.stderr}')
                    flag = False
                self.log.info('在线安装组件包成功')
            except Exception as e:
                self.log.error(f'在线安装组件包失败，错误信息：{e}')
                flag = False
        else:
            # 离线安装
            try:
                self.log.info('开始离线安装依赖包')
                install_packages = shellcmd(f'dpkg -i {self.res_dict["COMPONENTS_PATH"]}/*.deb')
                if install_packages.returncode:
                    self.log.error(f'离线安装组件包失败，错误信息：{install_packages.stderr}')
                    flag = False
                self.log.info('离线安装组件包成功')
            except Exception as e:
                self.log.error(f'离线安装组件包失败，错误信息：{e}')
                flag = False
        return flag


    def install(self):
        self.output_signal.emit(('info', f"进行install", 'green'))
    # 运行函数
    def run(self):
        try:
            self.running =True
            status = self.check_result_dict()
            print(f'check_result_dict{status}')
            if not status:
                return
            status = self.install_package()
            print(f'install_package{status}')
            if not status:
                return
            self.install()

        except Exception as e:
            print(str(e))

    def stop(self):
        self.running = False
        self.wait()