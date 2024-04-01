import wx.adv
import wx

class NotificationPopup:
    def __init__(self, title="", msg="", icon_path=""):
        self.title = title
        self.msg = msg
        self.icon_path = icon_path

    def show(self, duration=1):
        if self.title and self.msg:
            app = wx.App(False)
            icon = wx.Icon(self.icon_path, wx.BITMAP_TYPE_ICO)
            notification = wx.adv.NotificationMessage(self.title, self.msg)
            notification.SetIcon(icon)
            notification.SetFlags(wx.ICON_INFORMATION)
            notification.Show(timeout=duration)
            app.MainLoop()
        else:
            print("标题和消息不能为空！")


    def set_content(self, title, msg, icon_path):
        self.title = title
        self.msg = msg
        self.icon_path = icon_path


# 使用示例
# title = "校园网状态"
# msg = "校园网已连接！"
# icon_path = os.path.join(os.path.dirname(self.exe_path), "icos\\check.ico")
# popup = NotificationPopup(title, msg, icon_path)
# popup.show()
