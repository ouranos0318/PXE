# coding:utf-8
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QWidget
from qfluentwidgets import (NavigationBar, NavigationItemPosition, isDarkTheme, PopUpAniStackedWidget,  setThemeColor)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, TitleBar

from mode.service_interface import ServicePage
from mode.dhcp_interface import DHCPPage
from mode.auto_interface import AutoPage
from mode.deploy_interface import DeployPage
from mode.QThread_Install import Installer
import time
from PyQt5.QtGui import QColor



class AppLoger:
    def __init__(self, append_plain_text) -> None:
        self.appendPlainText = append_plain_text

    def info(self, text, color=None):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.appendPlainText(f"[INFO] [{current_time}] {text}", QColor(color))

    def error(self, text, color='red'):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.appendPlainText(f"[ERROR] [{current_time}] {text}",QColor(color))

    def warn(self, text, color='blue'):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.appendPlainText(f"[WARN] [{current_time}] {text}", QColor(color))

    def tip(self, text, color='green'):
        self.appendPlainText(f"{text}", QColor(color))



class Widget(QWidget):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class StackedWidget(QFrame):
    """ Stacked widget """

    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(self.currentChanged)

    def addWidget(self, widget):
        """ add widget to view """
        self.view.addWidget(widget)

    def widget(self, index: int):
        return self.view.widget(index)

    def setCurrentWidget(self, widget, popOut=False):
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(widget, True, False, 200, QEasingCurve.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.hBoxLayout.removeWidget(self.minBtn)
        self.hBoxLayout.removeWidget(self.maxBtn)
        self.hBoxLayout.removeWidget(self.closeBtn)

        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 20)
        self.hBoxLayout.insertWidget(1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)


        self.vBoxLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(0)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setAlignment(Qt.AlignTop)
        self.buttonLayout.addWidget(self.minBtn)
        self.buttonLayout.addWidget(self.maxBtn)
        self.buttonLayout.addWidget(self.closeBtn)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.vBoxLayout.addStretch(1)
        self.hBoxLayout.addLayout(self.vBoxLayout, 0)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))




class Window(FramelessWindow): # 继承AcrylicWindow后有亚克力效果
    conf_dict = {}
    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        #use dark theme mode
        # setTheme(Theme.DARK)
        # change the theme color
        setThemeColor('#28afe9')

        
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = StackedWidget(self)
        # create sub interface
        self.ServiceInterface = ServicePage(self)
        self.DHCPInterface = DHCPPage(self)
        self.AutoInterface = AutoPage(self)
        self.DeployInterface = DeployPage(self)
        # initialize layout
        self.initLayout()
        # add items to navigation interface
        self.initNavigation()
        self.initWindow()
        self.setMinimumSize(900, 760)  # 最小宽度 600，最小高度 400
        self.setMaximumSize(900, 760)  # 最大宽度 1600，最大高度 1200
        # 把日志写入到DeployInterface界面的PlainTextEdit控件中
        self.app_logger = AppLoger(self.DeployInterface.add_content_to_textedit)
        # 定义多线程类
        self.installer = None



    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.ServiceInterface, FIF.ADD_TO, '基础')
        self.addSubInterface(self.DHCPInterface, FIF.APPLICATION, 'DHCP')
        self.addSubInterface(self.AutoInterface, FIF.VIDEO, 'Auto')
        self.addSubInterface(self.DeployInterface, FIF.VIDEO, '部署')
        # 默认navigationBar高亮显示图标
        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.ServiceInterface.objectName())

    def initWindow(self):
        self.resize(750, 700)
        #self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowIcon(QIcon(':/qfluentwidgets/yhkylin.png'))
        self.setWindowTitle('PXE Deployment Tool')
        # 下一步按钮切换界面
        self.ServiceInterface.PrimaryPushButton_ServiceNext.clicked.connect(lambda: self.switchTo(self.DHCPInterface))
        self.DHCPInterface.PrimaryPushButton_ServiceNext.clicked.connect(lambda: self.switchTo(self.AutoInterface))
        self.AutoInterface.PrimaryPushButton_ServiceNext.clicked.connect(lambda: self.switchTo(self.DeployInterface))
        self.titleBar.setAttribute(Qt.WA_StyledBackground)
        desktop = QApplication.desktop().availableGeometry()
        _w, h = desktop.width(), desktop.height()
        self.move(_w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        # 调用设置QSS样式表的方法
        self.setQss()
        # 部署按钮执行操作
        self.DeployInterface.PrimaryPushButton.clicked.connect(self.onDeployButtonClicked)

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, selectedIcon=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            selectedIcon=selectedIcon,
            position=position,
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    
    def onDeployButtonClicked(self):
        self.DeployInterface.PlainTextEdit.clear()
        self.conf_dict = {}
        self.conf_dict.update(self.ServiceInterface.get_dict())
        self.conf_dict.update(self.DHCPInterface.get_dict())
        self.conf_dict.update(self.AutoInterface.get_dict())
        self.conf_dict.update(self.DeployInterface.get_dict())

        # begin = Installer(self.app_logger, self.conf_dict)
        # # begin.check()
        # print(self.conf_dict)
        # begin.deploy()
        # 创建多线程部署进程
        # 若之前的线程还在运行，先停止它
        if self.installer and self.installer.isRunning():
            self.installer.stop()
        self.installer = Installer(self.conf_dict)
        self.installer.output_signal.connect(self.UpdatePlainTextEdit)
        self.installer.error_signal.connect(self.HandleError)
        self.installer.finished_signal.connect(self.Finished)
        self.installer.start()


    def UpdatePlainTextEdit(self, text:tuple):
        level, text = text
        if level == 'tip':
            self.app_logger.tip(text, 'green')
        elif level == 'info':
            self.app_logger.info(text, 'green')
        elif level == 'warn':
            self.app_logger.warn(text, 'yellow')
        elif level == 'error':
            self.app_logger.error(text, 'red')

    def HandleError(self):
        print(text)

    def Finished(self):
        self.installer.stop()



    # def showMessageBox(self):
    #     w = MessageBox(
    #         '支持作者🥰',
    #         '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
    #         self
    #     )
    #     w.yesButton.setText('来啦老弟')
    #     w.cancelButton.setText('下次一定')

    #     if w.exec():
    #         QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)


    app = QApplication(sys.argv)
    w = Window()

    w.show()
    app.exec_()