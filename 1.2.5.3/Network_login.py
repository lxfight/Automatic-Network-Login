import os
import sys
import requests
from Network_PopWindow import NotificationPopup
from Network_Logs import Logger
from Network_encryption import decrypt
import Network_method as NM
import re


class NetworkLogin:
    def __init__(self):
        self.Retry_interval = 3
        self.Monitoring_interval = 3

        self.url = ""
        self.website = ""
        self.HomePageField = ""
        self.LoginPageField = ""
        self.Automatic_login = True
        self.window = None
        self.exe_path = os.path.abspath(sys.argv[0])
        self.popup = NotificationPopup()
        self.logger = Logger()
        self.ICONS_PATH = "icos\\"
        self.CHECK_ICON = "Check.ico"
        self.NETWORK_ICON = "Network.ico"
        self.ERROR_ICON = "error.ico"
        self.CROSS_ICON = "cross.ico"

    def _get_icon_path(self, icon_name):
        return os.path.join(os.path.dirname(self.exe_path), self.ICONS_PATH, icon_name)

    def change_Automatic_login(self, Automatic_login):
        self.Automatic_login = Automatic_login

    def read_setting(self):
        setting_path = os.path.join(os.path.dirname(self.exe_path), "setting")
        try:
            with open(setting_path, "rb") as f:
                for line in f:
                    line = line.decode().strip()
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "website":
                        self.website = value
                    elif key == "HomePageField":
                        self.HomePageField = value
                    elif key == "LoginPageField":
                        self.LoginPageField = value
                    elif key == "Automatic_login":
                        self.Automatic_login = value.lower() == "true"
        except FileNotFoundError:
            self.popup.set_content("setting文件丢失", "请使用强制重置功能",
                                   self._get_icon_path(self.ERROR_ICON))
            self.popup.show()

            NM.change_windowicon(self.window, self._get_icon_path(self.ERROR_ICON))
            self.logger.log_error("<ReadFileError>:The setting file content is lost")

    def is_valid_website(self):
        # 检查是否为空
        if not self.website:
            print("Website is empty")
            self.logger.log_error("<WebsiteError>:Url is empty")
            return False

        # 检查是否符合网址的要求
        url_pattern = re.compile(r"^(http|https)://.*/$", re.IGNORECASE)

        if re.match(url_pattern, self.website):
            return True
        else:
            print("Invalid website")
            self.logger.log_error("<WebsiteError>:Url format error")
            return False

    def is_internet_available(self):
        if not self.is_valid_website():
            self.popup.set_content("登录网址错误或丢失", "请使用强制重置功能",
                                   self._get_icon_path(self.ERROR_ICON))
            self.popup.show()
            return
        try:
            response = requests.get(self.website, timeout=1)
            if self.HomePageField in response.text:
                return "unconnected"
        except:
            return "ServiceException"
        return "Connected"

    def login_to_network(self):
        print("login to network")
        if not all(self.url):
            self.popup.set_content("Get请求url丢失", "请使用强制重置功能",
                                   self._get_icon_path(self.ERROR_ICON))
            self.popup.show()

            NM.change_windowicon(self.window, self._get_icon_path(self.ERROR_ICON))
            self.logger.log_event("<Network>:Get url is None")
        else:
            response = requests.get(self.url)
            if self.LoginPageField in response.text:
                print("响应内容中包含 '用户信息页' 字段")
                return True
            else:
                print("响应内容中不包含 '用户信息页' 字段")
                return False

    def url_decryption(self):
        url_file_path = os.path.join(os.path.dirname(self.exe_path), "url")
        key_file_path = os.path.join(os.path.dirname(self.exe_path), "url_key")
        try:
            with open(url_file_path, 'rb') as f:
                encrypted_url = f.read()
            with open(key_file_path, 'rb') as f:
                key = f.read()
            url = decrypt(encrypted_url, key)
        except FileNotFoundError:
            self.popup.set_content("url文件以及密钥文件丢失", "请使用强制重置功能",
                                   self._get_icon_path(self.ERROR_ICON))
            self.popup.show()

            NM.change_windowicon(self.window, self._get_icon_path(self.ERROR_ICON))

            self.logger.log_error("<Network>:url or key File Not Found Error")
            return None
        else:
            self.url = url

    def set_window(self, window):
        self.window = window

    def check_internet_connection(self):

        if self.Automatic_login:
            if self.is_internet_available() == "Connected":
                NM.restore_windowicon(self.window)
                return
            elif self.is_internet_available() == "unconnected":
                self.popup.set_content("网络连接状态", "校园网连接断开！", self._get_icon_path(self.CROSS_ICON))
                self.popup.show()
                NM.change_windowicon(self.window, self._get_icon_path(self.CROSS_ICON))
                self.logger.log_event("<Network>:Network disconnection")

                if self.login_to_network():
                    self.popup.set_content("网络连接状态", "校园网已连接！", self._get_icon_path(self.CHECK_ICON))
                    self.popup.show()
                    NM.restore_windowicon(self.window)
                    self.logger.log_event("<Network>:Connected")
                else:
                    self.popup.set_content("自动登录失败", "请不要使用网络全局代理", self._get_icon_path(self.ERROR_ICON))
                    self.popup.show()
                    NM.change_windowicon(self.window, self._get_icon_path(self.ERROR_ICON))
                    self.logger.log_event("<Network>:Service Exception")
            else:
                self.popup.set_content("服务异常", "建议使用强制重置功能", self._get_icon_path(self.ERROR_ICON))
                self.popup.show()
                NM.change_windowicon(self.window, self._get_icon_path(self.ERROR_ICON))
                self.logger.log_event("<Network>:Network disconnection")

        elif self.is_internet_available() == "Connected":
            NM.restore_windowicon(self.window)

        else:
            NM.change_windowicon(self.window, self._get_icon_path(self.NETWORK_ICON))
            self.logger.log_event("<Network>:Automatic login off")


