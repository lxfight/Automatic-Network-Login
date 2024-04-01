import sys
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon, QMainWindow
from PyQt5.QtGui import QIcon
import os
import webbrowser
from PIL import Image
from Network_Logs import Logger
import Network_Initialization as NI
import Network_method as NM
from tkinter import Tk, Label
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import shutil

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, LoginNetwork, pause_event, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.exe_path = os.path.abspath(sys.argv[0])
        self.icon = self.set_home_icon()
        self.image_path = os.path.join(os.path.dirname(self.exe_path), "png\\sponsor.png")

        self.original_icon = QIcon(self.icon)
        self.logger = Logger()

        self.LoginNetwork = LoginNetwork

        self.Automatic_login = self.LoginNetwork.Automatic_login
        self.internet_check_thread = None
        self.app = None
        self.pause_event = pause_event

        self.setIcon(icon)
        self.setToolTip("网络自动认证")

        # 创建菜单项
        self.menu = QMenu(parent)

        # 添加自动登录菜单项
        self.automatic_login_action = QAction('自动登录:{}'.format("开启" if self.Automatic_login else "关闭"), parent)
        self.automatic_login_action.triggered.connect(self.on_automatic_login_clicked)
        self.menu.addAction(self.automatic_login_action)

        # 添加赞助菜单项
        self.sponsor_action = QAction("赞助一下", parent)
        self.sponsor_action.triggered.connect(self.on_show_image_clicked)
        self.menu.addAction(self.sponsor_action)

        # 查看日志
        self.log_action = QAction("查看日志", parent)
        self.log_action.triggered.connect(self.on_log_clicked)
        self.menu.addAction(self.log_action)


        # 添加联系作者菜单项
        self.contact_author_menu = QMenu("联系作者", parent)

        # 添加GitHub子菜单项
        self.github_action = QAction("GitHub", parent)
        self.github_action.triggered.connect(self.open_github)
        self.contact_author_menu.addAction(self.github_action)

        # 添加Gitee子菜单项
        self.gitee_action = QAction("Gitee", parent)
        self.gitee_action.triggered.connect(self.open_gitee)
        self.contact_author_menu.addAction(self.gitee_action)

        self.menu.addMenu(self.contact_author_menu)

        # 添加重置菜单项
        self.reset_action = QAction("强制重置", parent)
        self.reset_action.triggered.connect(self.reset_login_script)
        self.menu.addAction(self.reset_action)

        # 添加强制退出菜单项
        self.force_exit_action = QAction("强制退出", parent)
        self.force_exit_action.triggered.connect(self.on_Force_out_clicked)
        self.menu.addAction(self.force_exit_action)

        # 添加退出菜单项
        self.exit_action = QAction("退出", parent)
        self.exit_action.triggered.connect(self.on_exit_clicked)
        self.menu.addAction(self.exit_action)

        self.setContextMenu(self.menu)
        self.activated.connect(self.on_activated)

    def set_app(self, app):
        self.app = app

    def set_internet_check_thread(self, internet_check_thread):
        self.internet_check_thread = internet_check_thread

    def set_Automatic_login(self, Automatic_login):
        self.Automatic_login = Automatic_login

    def update_automatic_login_action(self):
        self.automatic_login_action.setText(f'自动登录:{"开启" if self.Automatic_login else "关闭"}')

    def on_automatic_login_clicked(self):
        print("自动登录被点击")
        self.Automatic_login = not self.Automatic_login
        self.LoginNetwork.change_Automatic_login(self.Automatic_login)
        self.update_automatic_login_action()

    def on_show_image_clicked(self):
        print("赞助被点击")
        try:
            # image = Image.open(self.image_path)
            # image.show()
            root = Tk()
            root.title("赞助一下")

            # 获取屏幕尺寸
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            window_width = screen_width // 3
            window_height = screen_height // 2
            root.geometry(f"{window_width}x{window_height}")

            # 加载并缩放图片
            image = Image.open(self.image_path)
            image = image.resize((window_width, window_height))
            photo = ImageTk.PhotoImage(image)

            # 在窗口中显示图片
            label = tk.Label(root, image=photo)
            label.image = photo
            label.pack(expand=True, fill=tk.BOTH)

            # 运行主循环
            root.mainloop()
        except Exception as e:
            self.logger.log_error("<ReadFileError>:The sponsor png file content is lost")
            print("An error occurred:", e)

    # 暂停线程
    def pause_thread(self):
        self.pause_event.set()

    # 恢复线程
    def resume_thread(self):
        self.pause_event.clear()

    def reset_login_script(self):
        print("强制重置被点击")
        try:
            files_to_delete = ['setting', 'url', 'url_key']
            for file_name in files_to_delete:
                file_path = os.path.join(os.path.dirname(self.exe_path), file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.logger.log_event(f"<resetremove>:The {file_name} file be removed")
                    print(f"{file_name} 文件删除成功")
                else:
                    self.logger.log_error(f"<removeError>:The {file_name} file does not exist")
                    print(f"{file_name} 文件不存在")
        except Exception as e:
            self.logger.log_error(f"<removeError>:remove error")
        finally:
            self.on_exit_clicked()
            # # 暂停登录脚本
            # self.pause_thread()
            # if NI.main()[0]:
            #     self.resume_thread()
            # else:
            #     NM.stop(self.internet_check_thread, self.app)
    
    def on_log_clicked(self):
        print("日志被点击")
        self.logger.open_log_file()
    
    def on_Force_out_clicked(self):
        print("强制退出被点击")
        NM.Force_Out()

    def on_exit_clicked(self):
        print("退出被点击")
        NM.stop(self.internet_check_thread, self.app)

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            print("左键被点击")
            self.select_icon_file()

    def open_github(self):
        webbrowser.open("https://github.com/lxfight")

    def open_gitee(self):
        webbrowser.open("https://gitee.com/goodliandge")

    def change_icon(self, new_icon):
        self.setIcon(QIcon(new_icon))

    def restore_icon(self):
        # 将系统托盘图标还原为最初的图标
        self.setIcon(self.original_icon)

    def select_icon_file(self):
        Boot = tk.Tk()
        Boot.withdraw()  # 隐藏主窗口

        # 打开文件对话框，让用户选择图标文件
        icon_file_path = filedialog.askopenfilename(
            title="选择你想要的图标文件",
            filetypes=(("Icon files", "*.ico"), ("All files", "*.*"))
        )
        if icon_file_path:
            target_path = os.path.join(os.path.dirname(self.exe_path), "icos", "NEWICON.ico")
            shutil.copy2(icon_file_path, target_path)
            self.HOMEICON = target_path
            self.original_icon = QIcon(target_path)
            self.restore_icon()
        Boot.destroy()
        Boot.mainloop()
    def set_home_icon(self):
        new_icon_path = os.path.join(os.path.dirname(self.exe_path), "icos", "NEWICON.ico")
        ahnu_icon_path = os.path.join(os.path.dirname(self.exe_path), "icos", "AHNU.ico")

        if os.path.exists(new_icon_path):
            return new_icon_path
        else:
            return ahnu_icon_path

class MainWindow(QMainWindow):
    def __init__(self, LoginNetwork, pause_event):
        super().__init__()
        self.setWindowTitle("网络自动认证")
        self.setGeometry(100, 100, 400, 300)
        self.LoginNetwork = LoginNetwork
        self.pause_event = pause_event
        self.exe_path = os.path.abspath(sys.argv[0])

        self.tray_icon = SystemTrayIcon(self.LoginNetwork,self.pause_event,
                                        QIcon(os.path.join(os.path.dirname(self.exe_path), "icos\\AHNU.ico")), self)
        self.tray_icon.update_automatic_login_action()
        self.tray_icon.show()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#
#     sys.exit(app.exec_())
