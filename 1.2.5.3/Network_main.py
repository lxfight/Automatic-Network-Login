import Network_Initialization as NI
import Network_SystemTray as NS
import Network_PopWindow as NP
import Network_login as NL
import Network_Logs as NLogs
import Network_method as NM
import os
import sys
import subprocess
import threading


class NetworkForAHNU:
    def __init__(self):
        self.LoginNetwork = NL.NetworkLogin()
        self.popup = NP.NotificationPopup()
        self.logger = NLogs.Logger()
        self.exe_path = os.path.abspath(sys.argv[0])
        self.internet_check_thread = None
        self.app = None
        self.window = None

        self.HomePageField = ""
        self.LoginPageField = ""
        self.Automatic_login = True

        self.pause_event = threading.Event()

    def get_date(self):
        self.HomePageField = self.LoginNetwork.HomePageField
        self.LoginPageField = self.LoginNetwork.LoginPageField
        self.Automatic_login = self.LoginNetwork.Automatic_login

    def start(self):
        self.LoginNetwork.url_decryption()
        self.LoginNetwork.read_setting()
        self.get_date()

        self.app = NS.QApplication(sys.argv)
        self.window = NS.MainWindow(self.LoginNetwork, self.pause_event)
        self.LoginNetwork.window = self.window
        self.window.tray_icon.app = self.app
        self.window.tray_icon.internet_check_thread = self.internet_check_thread
        self.window.tray_icon.pause_event = self.pause_event

        self.internet_check_thread = threading.Thread(
            target=NM.internet_connection,
            args=(self.exe_path, self.popup, self.LoginNetwork, self.logger, self.pause_event),
            daemon=True
        )
        self.internet_check_thread.start()

        sys.exit(self.app.exec_())


if __name__ == "__main__":
    monitor = NetworkForAHNU()
    if NM.check_login_script(monitor.exe_path):
        monitor.start()
    else:
        if os.path.exists(os.path.join(os.path.dirname(monitor.exe_path), "LoginFileCorrelation.docx")):
            subprocess.call(["start", "", os.path.join(os.path.dirname(monitor.exe_path), "LoginFileCorrelation.docx")],
                            shell=True)
        if NI.main()[0]:
            monitor.start()
        else:
            sys.exit(0)
