import logging
import os
import sys

class Logger:
    def __init__(self, log_filename="network_login.log", log_level=logging.DEBUG):
        self.exe_path = os.path.abspath(sys.argv[0])
        self.log_file = os.path.join(os.path.dirname(self.exe_path), log_filename)
        self.log_level = log_level
        self.setup_logging()

    def setup_logging(self):
        # 创建日志记录器
        self.logger = logging.getLogger('network_login')
        self.logger.setLevel(self.log_level)

        # 创建一个文件处理程序来将日志写入文件
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)

        # 创建一个格式化器，并将其添加到处理程序
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 添加文件处理程序到记录器
        self.logger.addHandler(file_handler)

    def log_event(self, message):
        # 记录事件到日志文件
        self.logger.info(message)

    def log_error(self, message):
        # 记录错误到日志文件
        self.logger.error(message)

    def open_log_file(self):
        os.startfile(self.log_file)


# 使用示例
# log_filename = 'network_login.log'
# logger = Logger(log_filename)
#
# # 记录事件
# logger.log_event("Network connected successfully")
#
# # 记录错误
# logger.log_error("Error occurred: Some error message")
