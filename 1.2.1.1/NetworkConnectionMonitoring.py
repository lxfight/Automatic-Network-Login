import os
import subprocess
import sys
import time
import pystray
from pystray import MenuItem as item
from PIL import Image
import requests
import threading
from win10toast import ToastNotifier
import tkinter as tk


class InternetConnectionMonitor:
    def __init__(self):
        self.internet_check_thread = threading.Thread(target=self.check_internet_connection)
        self.icon = None
        self.toaster = ToastNotifier()
        self.login_url = ""
        self.Automatic_login = True
        self.keep_running = True
        self.Retry_interval = 3
        self.Monitoring_interval = 10
        self.menu = [
            item('自动登录:{}'.format("开启" if self.Automatic_login else "关闭"), self.on_automatic_login_clicked),
            item('赞助一下', self.on_show_image_clicked),
            item('重置', self.reset_login_script),
            item('强制退出', self.on_Force_out_clicked),
            item('退出', self.on_exit_clicked)
        ]
        self.exe_path = os.path.abspath(sys.argv[0])

    def update_menu(self):
        self.menu = [
            item('自动登录:{}'.format("开启" if self.Automatic_login else "关闭"), self.on_automatic_login_clicked),
            item('赞助一下', self.on_show_image_clicked),
            item('重置',self.reset_login_script),
            item('强制退出', self.on_Force_out_clicked),
            item('退出', self.on_exit_clicked)
        ]
        self.icon.menu = self.menu
    def Initialize_URL(self):
        self.get_login_url()
        if self.login_url != "":
            self.write_to_vbs()
            return True
        else:
            self.toaster.show_toast("url提交不能为空！！！", msg='仔细查看word中的内容！')
            return False
    def reset_login_script(self):
        script_path = os.path.join(os.path.dirname(self.exe_path), "login.vbs")
        if os.path.exists(script_path):
            os.remove(script_path)
            # print("login.vbs脚本已成功删除。")
            self.Initialize_URL()
        else:
            pass
            #print("login.vbs脚本不存在，无需删除。")
    def on_show_image_clicked(self):
        image_path = os.path.join(os.path.dirname(self.exe_path), "Collection_code.png")
        if os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image.show()
            except Exception as e:
                pass
        else:
            pass

    def on_exit_clicked(self):
        self.icon.stop()
        self.keep_running = False
        if self.internet_check_thread and self.internet_check_thread.is_alive():
            self.internet_check_thread.join()
        sys.exit(0)

    def on_Force_out_clicked(self):
        self.icon.stop()
        os._exit(0)

    def on_automatic_login_clicked(self):
        self.Automatic_login = not self.Automatic_login
        self.update_menu()

    def write_to_vbs(self):
        vbs_content = '''\
        url="{}"
        set http = CreateObject("MSXML2.XMLHTTP")
        http.open "GET", url, False
        http.send
        '''.format(self.login_url)

        with open("login.vbs", "w") as f:
            f.write(vbs_content)

    def get_login_url(self):
        window = tk.Tk()
        window.title("login")

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        window_width = 300
        window_height = 80
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        window.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))
        window.lift()

        label = tk.Label(window, text="请输入word文件中提到的url：")
        label.pack()

        entry = tk.Entry(window)
        entry.pack()

        def on_submit():
            self.login_url = entry.get()
            window.destroy()

        submit_button = tk.Button(window, text="提交", command=on_submit)
        submit_button.pack()

        window.mainloop()

    def check_login_script(self):
        script_path = os.path.join(os.path.dirname(self.exe_path), "login.vbs")
        if os.path.exists(script_path):
            if os.path.getsize(script_path) > 0:
                return True
        return False

    def is_internet_available(self):
        url = "http://www.baidu.com"
        try:
            response = requests.get(url, timeout=1)
            if "上网登录页" in response.text:
                return "unconnected"
        except:
            return "ServiceException"
        return "Connected"

    def login_to_network(self):
        script_path = os.path.join(os.path.dirname(self.exe_path), "login.vbs")
        result = subprocess.call(["cscript", script_path])
        return result == 0

    def update_tray_icon(self):

        status = self.is_internet_available()
        self.icon.title = "Internet Connection Monitor"
        self.icon.menu = self.menu
        self.icon.tooltip = "互联网连接状态: " + status

        if status == "Connected":
            self.icon.icon = Image.open(os.path.join(os.path.dirname(self.exe_path), "AHNU.ico"))
        elif status == "unconnected":
            self.icon.icon = Image.open(os.path.join(os.path.dirname(self.exe_path), "Cross.ico"))
        elif status == "ServiceException":
            self.icon.icon = Image.open(os.path.join(os.path.dirname(self.exe_path), "Questionmark.ico"))

    def create_tray_icon(self):

        initial_icon = Image.open(os.path.join(os.path.dirname(self.exe_path), "Network.ico"))
        self.icon = pystray.Icon("Internet Connection Monitor", initial_icon, "Internet Connection Monitor", self.menu)
        self.update_tray_icon()
        self.icon.run()

    def check_internet_connection(self):
        time.sleep(0.3)
        while self.keep_running:
            if self.is_internet_available() != "Connected":
                self.update_tray_icon()
                if self.Automatic_login:
                    result = self.login_to_network()
                    if result:
                        self.toaster.show_toast("校园网状态",
                                                msg="校园网已连接！",
                                                duration=3,
                                                icon_path=os.path.join(os.path.dirname(self.exe_path), "Tips.ico"),
                                                threaded=False)
                    else:
                        self.toaster.show_toast("自动登录服务异常",
                                                msg="自动登录脚本异常！！！",
                                                duration=3,
                                                icon_path=os.path.join(os.path.dirname(self.exe_path),
                                                                       "Questionmark.ico"),
                                                threaded=False)
                    time.sleep(self.Retry_interval)
                else:
                    while not self.Automatic_login:
                        time.sleep(1)

            else:
                self.update_tray_icon()
                time.sleep(self.Monitoring_interval)

    def main(self):
        self.internet_check_thread.start()
        self.create_tray_icon()


if __name__ == "__main__":
    monitor = InternetConnectionMonitor()
    if monitor.check_login_script():
        monitor.main()
    else:
        if os.path.exists(os.path.join(os.path.dirname(monitor.exe_path), "LoginFileCorrelation.docx")):
            subprocess.call(["start", "", os.path.join(os.path.dirname(monitor.exe_path), "LoginFileCorrelation.docx")],
                            shell=True)
        if monitor.Initialize_URL():
            monitor.main()
        else:
            sys.exit(0)

