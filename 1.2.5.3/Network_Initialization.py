import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QWidget, \
    QDesktopWidget, QMessageBox
from PyQt5.QtGui import QIcon
from Network_encryption import encrypt, generate_key


def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    status = app.exec_()
    submitted_successfully = window.submitted_successfully
    return submitted_successfully, status



class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        icon_path = os.path.join(os.getcwd(), "icos", "AHNU.ico")

        self.setWindowTitle("初始化设置")
        self.setGeometry(100, 100, 400, 400)
        self.center()
        self.setWindowIcon(QIcon(icon_path))
        self.submitted_successfully = False
        self.submitted_via_button = False

        # 创建主widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 创建布局
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # 创建标题
        title_label = QLabel("初始化设置")
        title_label.setStyleSheet("font-weight: bold; font-size: 20px; text-align: center;")
        layout.addWidget(title_label)

        # 创建输入框和标签
        url_label = QLabel("请求URL:")
        self.url_input = QLineEdit()
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)

        Login_website = QLabel("登录网址:")
        self.website_input = QLineEdit()
        layout.addWidget(Login_website)
        layout.addWidget(self.website_input)


        identifier_label = QLabel("认证首页名称:")
        self.identifier_input = QLineEdit()
        layout.addWidget(identifier_label)
        layout.addWidget(self.identifier_input)

        success_label = QLabel("认证成功返回字段:")
        self.success_input = QLineEdit()
        layout.addWidget(success_label)
        layout.addWidget(self.success_input)

        # 创建勾选框
        self.autologin_checkbox = QCheckBox("默认开启自动登录")
        layout.addWidget(self.autologin_checkbox)

        # 创建按钮
        submit_button = QPushButton("提交")
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

        # 设置整体样式
        main_widget.setStyleSheet("background-color: #f0f0f0; padding: 20px;")


    def center(self):
        # 获取窗口的尺寸和分辨率
        screen = QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)



    def submit(self):
        # 获取输入框和勾选框的内容
        url = self.url_input.text()
        website = self.website_input.text()
        identifier = self.identifier_input.text()
        success = self.success_input.text()
        autologin_checked = self.autologin_checkbox.isChecked()

        if not all([url, website, identifier,success]):
            QMessageBox.warning(self, "警告", "请输入完整信息！")
            return False

        current_dir = os.getcwd()

        website = f"website:{website}\n".encode('utf-8')
        identifier = f"HomePageField:{identifier}\n".encode('utf-8')
        success = f"LoginPageField:{success}\n".encode('utf-8')
        autologin_checked = f"Automatic_login:{'True' if autologin_checked else 'False'}\n".encode('utf-8')

        # 生成密钥
        url_key = generate_key()

        # 将原始内容加密
        url = encrypt(url, url_key)


        url_path = os.path.join(current_dir, "url")
        key_path = os.path.join(current_dir, "url_key")
        setting_path = os.path.join(current_dir, "setting")

        with open(setting_path, "wb") as f:
            f.write(website)
            f.write(identifier)
            f.write(success)
            f.write(autologin_checked)

        with open(url_path, "wb") as f:
            f.write(url)

        with open(key_path, "wb") as f:
            f.write(url_key)

        print("设置已加密保存到文件。")
        self.submitted_successfully = True
        self.submitted_via_button = True
        self.close()

    def closeEvent(self, event):
        if not self.submitted_via_button:
            # 窗口关闭时触发的事件
            result = QMessageBox.question(self, "确认", "确定要关闭窗口吗？",
                                          QMessageBox.Yes | QMessageBox.No)
            if result == QMessageBox.Yes:
                self.submitted_successfully = False
                event.accept()
            else:
                event.ignore()

