
class Installer():    
    def __init__(self, logobject, res_dict):
        self.log = logobject
        self.res_dict = res_dict
        
        
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