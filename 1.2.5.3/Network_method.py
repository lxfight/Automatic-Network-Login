import os
import time
import sys





def stop(internet_check_thread, app):
    if internet_check_thread and internet_check_thread.is_alive():
        internet_check_thread.join()
    app.quit()
    os._exit(0)


def Force_Out():
    # 强制退出
    os._exit(0)


def check_login_script(exe_path):
    files_to_check = ['setting', 'url', 'url_key']

    for file_name in files_to_check:
        file_path = os.path.join(os.path.dirname(exe_path), file_name)

        if not os.path.isfile(file_path):
            return False

    return True


def change_windowicon(window, icon_path):
    window.tray_icon.change_icon(icon_path)


def restore_windowicon(window):
    window.tray_icon.restore_icon()


def internet_connection(exe_path, popup, LoginNetwork, logger, pause_event):
    if not all([LoginNetwork.HomePageField, LoginNetwork.LoginPageField]):
        popup.set_content("setting文件内容丢失", "请使用强制重置功能",
                          os.path.join(os.path.dirname(exe_path), "icos\error.ico"))
        popup.show()
        logger.log_error("<Initialize>:The setting file content is lost")
        return
    try:
        while not pause_event.is_set():
            # print(pause_event)
            LoginNetwork.check_internet_connection()
            if pause_event.wait(timeout=1):
                continue
            time.sleep(3)
    except Exception as e:
        logger.log_error(f"<LoopError>:Error occurred during internet connection check: {e}")
