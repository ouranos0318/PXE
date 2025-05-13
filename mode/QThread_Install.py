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

    def deploy_dhcp(self):
        flag = True
        # 配置网卡绑定
        try:
            self.log.info('开始配置网卡绑定')
            interface_name = self.res_dict['NET_INTER_NAME']
            with open('/etc/default/isc-dhcp-server', 'r') as f:
                lines = f.readlines()
            # 修改 INTERFACESv4 的值
            with open('/etc/default/isc-dhcp-server', 'w') as f:
                for line in lines:
                    if line.startswith('INTERFACESv4='):
                        f.write(f"INTERFACESv4=\"{interface_name}\"\n")
                    else:
                        f.write(line)
            self.log.info(f"网卡绑定配置成功，INTERFACESv4=\"{interface_name}\"")
        except Exception as e:
            self.log.error(f'配置网卡绑定失败，错误信息：{e}')
            flag = False

        # 配置DHCP文件
        try:
            self.log.info('开始配置DHCP')
            net_ip = self.res_dict['NET_INTER_IP']
            network_segment = '.'.join(net_ip.split('.')[:3])
            net_boot = 'x86_64-efi/netbootx64.efi' if self.res_dict['ARCH'] == "X86" else 'arm64-efi/netbootaa64.efi'
            dhcp_config = (
                "Option space PXE;\n"
                "allow booting;\n"
                "allow bootp;\n"
                f"subnet {network_segment}.0 netmask 255.255.255.0 {{\n"
                f"    range {self.res_dict['START_IP']} {self.res_dict['END_IP']};\n"
                f"    option subnet-mask 255.255.255.0;\n"
                f"    option routers {network_segment}.1;\n"
                f"    next-server {self.res_dict['NET_INTER_IP']};\n"
                f'    filename "{net_boot}";\n'
                "}\n"
            )
            with open('/etc/dhcp/dhcpd.conf', 'w') as f:
                f.write(dhcp_config)
            self.log.info('配置DHCP成功')
        except Exception as e:
            self.log.error(f'配置DHCP失败,错误信息：{e}')
            flag = False
        return flag

    def deploy_nfs(self):
        flag = True
        # 配置NFS
        try:
            self.log.info('开始配置NFS')
            nfs_config = f"/opt/nfs *(ro,async,no_subtree_check)\n"
            with open('/etc/exports', 'a') as f:
                f.write(nfs_config)
            shellcmd('exportfs -a')
            self.log.info('配置NFS成功')
        except Exception as e:
            self.log.error(f'配置NFS失败,错误信息：{e}')
            flag = False
        return flag

    def mount_iso(self):
        flag = True
        # 挂在ISO镜像
        try:
            self.log.info('开始挂载ISO镜像')
            mount_iso = shellcmd(f'mount -o loop {self.res_dict["ISO_PATH"]} /mnt')
            if mount_iso.returncode:
                self.log.error(f'挂载ISO镜像失败,错误信息：{mount_iso.stderr}')
                flag = False
            else:
                self.log.info('挂载ISO镜像成功')
        except Exception as e:
            self.log.error(f'挂载ISO镜像失败,错误信息：{e}')
            flag = False
        return flag

    def copy_iso(self):
        flag = True
        # 复制镜像
        try:
            self.iso_dir = 'arm64-efi' if self.res_dict['ARCH'] == "ARM" else 'x86_64-efi'
            self.log.info('开始复制镜像')
            if not os.path.exists(f'/opt/nfs/{self.iso_dir}'):
                os.makedirs(f'/opt/nfs/{self.iso_dir}')
            copy_iso = shellcmd(f'cp -arp /mnt/. /opt/nfs/{self.iso_dir}/')
            if copy_iso.returncode:
                self.log.error(f'复制镜像失败,错误信息：{copy_iso.stderr}')
                flag = False
            self.log.info('复制镜像成功')
        except Exception as e:
            self.log.error(f'复制镜像失败,错误信息：{e}')
            flag = False
        return flag

    def config_installer(self):
        flag = True
        if self.res_dict['IMPORT']:
            self.config.read(self.res_dict['IMPORT_PATH'], encoding='utf-8')
            self.log.info('开始导入配置文件')
            if not self.config.read(self.res_dict['IMPORT_PATH'], encoding='utf-8'):
                self.log.error(f"导入配置文件失败,错误信息：{self.config.read(self.res_dict['IMPORT_PATH'])}")
                flag = False
            self.log.info('导入配置文件成功')
        else:
            self.config.read('default.cfg', encoding='utf-8')
            # 设置installer.cfg文件
            # [Encrypty]
            self.config.set('Encrypty','encrypty',str(self.res_dict['ENCRYPTY']).lower())
            self.config['Encrypty']['encryptypwd'] = f"@ByteArray({self.res_dict['ENCRYPTY_PWD']})"
            self.config['Encrypty']['lvm'] = str(self.res_dict['LVM']).lower()
            # [config]
            self.config['config']['autologin'] = '1' if self.res_dict['AUTOLOGIN'] else '0'
            self.config['config']['automatic-installation'] = '1' if self.res_dict['AUTOMATIC'] else '0'
            self.config['config']['devpath'] = self.res_dict['DEV_PATH']
            self.config['config']['enable-swapfile'] = str(self.res_dict['SWAPFILE']).lower()
            self.config['config']['factory-backup'] = '1' if self.res_dict['BACKUP'] else '0'
            self.config['config']['username'] = self.res_dict['USERNAME']
            self.config['config']['password'] = f"@ByteArray({self.res_dict['USERPWD']})"
            self.config['config']['reboot'] = '1' if self.res_dict['REBOOT'] else '0'
            self.config['config']['username'] = str(self.res_dict['USERNAME']).lower()
            self.config['config']['data-device'] = self.res_dict['DATA_DEVICE_PATH']
            self.config['config']['oem-config'] = str(self.res_dict['OOBE']).lower()
            self.config['config']['data-unformat'] = str(self.res_dict['UNFORMAT']).lower()
            # [custom-partitions]
            self.config['custompartition']['disk-custom'] =  str(self.res_dict['CUSTOM']).lower()
            self.config['custompartition']['custom-partitions'] =  f"\"{self.res_dict['CUSTOM_PARTITION']['custom-partitions']}\""
            self.config['custompartition']['custom-efi'] =  f"\"{self.res_dict['CUSTOM_PARTITION']['custom-efi']}\""
            self.config['custompartition']['custom-boot'] = f"\"{self.res_dict['CUSTOM_PARTITION']['custom-boot']}\""
            self.config['custompartition']['custom-root'] =  f"\"{self.res_dict['CUSTOM_PARTITION']['custom-root']}\""
            self.config['custompartition']['custom-backup'] =  f"\"{self.res_dict['CUSTOM_PARTITION']['custom-backup']}\""
            self.config['custompartition']['custom-data'] =  f"\"{self.res_dict['CUSTOM_PARTITION']['custom-data']}\""
            self.config['custompartition']['custom-swap'] =  f"\"{self.res_dict['CUSTOM_PARTITION']['custom-swap']}\""
        # 写入ky-installer.cfg
        try:
            self.log.info('开始写入配置文件')
            installer_path = os.path.join('/opt/nfs/',self.iso_dir, 'ky-installer.cfg')
            with open(installer_path, 'w', encoding='utf-8') as file:
                self.config.write(file)  # type: ignore
                self.log.info('写入配置文件成功')
        except Exception as e:
            self.log.error(f'写入配置文件失败,错误信息：{e}')
            flag = False
        return flag

    def deploy_tftp(self):
        flag = True
        try:
            # 创建TFTP目录
            if not os.path.exists('/srv/tftp'):
                os.makedirs('/srv/tftp')
            # 解压启动文件
            tar_file = shellcmd(f"tar zxvf {self.iso_dir}.tar.gz -C /srv/tftp/")
            if tar_file.returncode:
                self.log.error(f'解压启动文件,错误信息：{tar_file.stderr}')
                flag = False
            self.log.info(f'解压{self.iso_dir}.tar.gz成功')
            # 创建/srv/tftp/{self.iso_dir}/casper目录
            self.log.info(f'创建/srv/tftp/{self.iso_dir}/casper目录')
            if not os.path.exists(f'/srv/tftp/{self.iso_dir}/casper'):
                os.makedirs(f'/srv/tftp/{self.iso_dir}/casper')
                self.log.info(f'创建/srv/tftp/{self.iso_dir}/casper目录')
            # 拷贝vmlinuz和initrd.lz
            cp_vmlinuz_initrd = shellcmd(
                f'cp /mnt/casper/vmlinuz /mnt/casper/initrd.lz /srv/tftp/{self.iso_dir}/casper/')
            if cp_vmlinuz_initrd.returncode:
                self.log.error(f'复制vmlinuz和initrd.lz失败,错误信息：{cp_vmlinuz_initrd.stderr}')
                flag = False
            self.log.info('复制vmlinuz和initrd.lz成功')
            # 配置grub文件
            grub_file = (
                f'menuentry "Install Kylin-Desktop-Auto" {{\n'
                f"linux ${{root}}/casper/vmlinuz boot=casper locale=zh_CN quiet splash audit =0 ip=dhcp netboot=nfs nfsroot= {self.res_dict['NET_INTER_IP']}:/opt/nfs/{self.iso_dir}/ security= a utomatic-ubiquity"
                f"initrd ${{root}}/casper/initrd.lz\n}}"
            )
            with open(f'/srv/tftp/{self.iso_dir}/boot/grub/grub.cfg', 'w') as f:
                f.write(grub_file)
                self.log.info('配置grub文件成功')
        except Exception as e:
            self.log.error(f'TFTP配置失败,错误信息：{e}')
            flag = False
        return flag

    def restart_service(self):
        flag = True
        try:
            # 重启服务
            self.log.info('开始重启服务')
            restart_dhcp = shellcmd('systemctl restart isc-dhcp-server')
            restart_nfs = shellcmd('systemctl restart nfs-server')
            restart_tftp = shellcmd('systemctl restart tftpd-hpa')
            if restart_dhcp.returncode or restart_nfs.returncode or restart_tftp.returncode:
                self.log.error(f'重启服务失败,错误信息：{restart_dhcp.stderr}')
                flag = False
            else:
                self.log.info('重启服务成功')
        except Exception as e:
            self.log.error(f'重启服务失败,错误信息：{e}')
            flag = False
        return flag
    # 运行函数
    def run(self):
        try:
            self.running = True
            methods_to_run = [
                self.check_result_dict,
                self.install_package,
                self.deploy_dhcp,
                self.deploy_nfs,
                self.mount_iso,
                self.copy_iso,
                self.config_installer,
                self.deploy_tftp,
                restart_service
            ]

            for method in methods_to_run:
                status = method()
                print(f'{method.__name__} => {status}')
                if not status:
                    return

            self.log.info('所有配置完成')
        except Exception as e:
            self.log.error(f'运行过程中出现异常,错误信息：{e}')
            print(str(e))

    def stop(self):
        self.running = False
        self.wait()