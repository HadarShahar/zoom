"""
    Hadar Shahar

"""
import ctypes
import win32con
import win32gui
import win32process
import subprocess
import time
from PyQt5.QtCore import QThread, pyqtSignal


class RemoteWindow(QThread):
    """
    Definition of the class RemoteWindow.

    This class must inherit from QtCore.QThread and not threading.Thread
    because new signal is defined in its subclasses.
    New signals should only be defined in sub-classes of QObject.
    """

    # time to sleep after the window is created, to give it time to appear
    INITIAL_DELAY_TIME = 0.1

    def __init__(self, program_name: str):
        """ Constructor. """
        super(RemoteWindow, self).__init__()
        self.program_name = program_name
        self.is_open = False
        self.hwnd = None

    def create_window(self):
        """ Creates the window and gets its handle. """
        process = subprocess.Popen([self.program_name])
        # sleep to give the window time to appear
        time.sleep(RemoteWindow.INITIAL_DELAY_TIME)
        # TODO check if could be several handles and why
        self.hwnd = RemoteWindow.get_hwnds_for_pid(process.pid)[0]

        print('created window:', repr(win32gui.GetWindowText(self.hwnd)))
        win32gui.SetWindowText(self.hwnd, 'Remote Window')
        self.is_open = True

    def close(self):
        """ Closes the window. """
        win32gui.SendMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
        self.is_open = False

    @staticmethod
    def print_last_error():
        """ Prints the last error. """
        error = ctypes.windll.kernel32.GetLastError()
        print(ctypes.WinError(error))

    @staticmethod
    def get_hwnds_for_pid(pid):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and \
                    win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds
