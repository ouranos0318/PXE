class Installer():
    def __init__(self, logobject):
        self.log = logobject

    def check(self, res_dict):
        self.log.info("开始检查配置")
        self.log.warn("配置错误")