import subprocess
import time
import win32con
import win32gui
import win32process
import win32clipboard
import ctypes
from ctypes.wintypes import WPARAM, LPARAM
from registry_utils import get_reg_local_machine

WORD_PATH = get_reg_local_machine(r'SOFTWARE\Microsoft\Windows\CurrentVersion'
                                  r'\App Paths\Winword.exe', '')
user32 = ctypes.WinDLL("User32.dll")


def get_hwnds_for_pid(pid):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


def write_text_notepad(hwnd, text):
    # look for the child window of class Edit - the editor
    hwnd_edit = user32.FindWindowExW(hwnd, None, "Edit", None)
    # write on editor
    user32.SendMessageW(hwnd_edit, win32con.WM_SETTEXT, 0, text)


def write_text_word(hwnd, text):
    # "listdir.exe" program

    hwnd_edit = user32.FindWindowExW(hwnd, None, "_WwG", None)
    print('hwnd_edit:', hwnd_edit)
    print(win32gui.GetWindowText(hwnd_edit))
    print(repr(win32gui.GetClassName(hwnd_edit)))
    # user32.SendMessageW(hwnd_edit, win32con.WM_SETTEXT, 0, text)


def read_clipboard():
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    return data

# HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, WPARAM, LPARAM)
# @HOOKPROC
# def hook_proc(nCode, wParam, lParam):
#     print(nCode, wParam, lParam)


def main():
    program = subprocess.Popen([WORD_PATH])
    # sleep to give the window time to appear
    time.sleep(3)
    pid = program.pid

    hwnd = get_hwnds_for_pid(pid)[0]
    print(win32gui.GetWindowText(hwnd))
    write_text_word(hwnd, 'hello world')

    # current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
    # hook = user32.SetWindowsHookExW(win32con.WH_CALLWNDPROC, hook_proc,
    #                                 None, 0)
    # print(hook)

    error = ctypes.windll.kernel32.GetLastError()
    print(ctypes.WinError(error))
    input('press any key to exit...')
    win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)


if __name__ == '__main__':
    main()
