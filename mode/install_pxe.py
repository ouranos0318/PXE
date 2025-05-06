from configparser import ConfigParser


class Installer():    
    def __init__(self, logobject, res_dict):
        self.log = logobject
        self.res_dict = res_dict
        self.config = ConfigParser()
        self.config.read('default.cfg')
    
    # 检查ip是否在同一网段
    def ipCheck(self, ip1, ip2):
        ip1_parts = ip1.split('.')
        ip2_parts = ip2.split('.')
        if len(ip1_parts) != 4 or len(ip2_parts) != 4:
            return False
        # 比较前三个网段
        for i in range(3):
            if ip1_parts[i] != ip2_parts[i]:
                return False      

    def check(self):
        Modifier = '*' * 10
        # 检查service_interface配置项
        self.log.info(f"{Modifier}检查基础页配置项{Modifier}")
        if not self.res_dict['ISO_PATH']:
            self.log.error("ISO路径不能为空,进程停止")
            return False
        if not self.res_dict['ONLINE_INSTALL']:
            if not self.res_dict['COMPONENTS_PATH']:
                self.log.error("选择离线安装时,组件路径不能为空,进程停止")
                return False

        # 检查deploy_interface配置项
        self.log.info(f"{Modifier}检查DHC页配置项{Modifier}")

        if self.res_dict['NET_INTER_IP'] and not self.res_dict['NET_INTER_IP'].startwith('169.254.'):
            self.log.error("网络接口IP不为空时,起始IP和结束IP不能为空,进程停止")
            return False
            if not self.ipCheck(self.res_dict['NET_INTER_IP'], self.res_dict['START_IP']):
                self.log.error("网络接口IP与起始IP不在同一网段,进程停止")
                return False
            if not self.ipCheck(self.res_dict['NET_INTER_IP'], self.res_dict['END_IP']):
                self.log.error("网络接口IP与结束IP不在同一网段,进程停止")
                return False
            if self.res_dict['START_IP'] > self.res_dict['END_IP']:
                elf.log.error("起始IP大于结束IP,进程停止")
                return False
        else:
            self.log.error("网卡IP为空或为169.254.xxx.xxx,进程停止")
            return False

        # 检查auto_interface配置项
        self.log.info(f"{Modifier}检查AUTO页配置项{Modifier}")

        