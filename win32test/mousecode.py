# https://stackoverflow.com/questions/31379169/setting-up-a-windowshook-in-python-ctypes-windows-api

from ctypes import *
from ctypes.wintypes import *
import win32con

user32 = WinDLL('user32', use_last_error=True)

MSG_TEXT = {
    win32con.WM_MOUSEMOVE: 'WM_MOUSEMOVE',
    win32con.WM_LBUTTONDOWN: 'WM_LBUTTONDOWN',
    win32con.WM_LBUTTONUP: 'WM_LBUTTONUP',
    win32con.WM_RBUTTONDOWN: 'WM_RBUTTONDOWN',
    win32con.WM_RBUTTONUP: 'WM_RBUTTONUP',
    win32con.WM_MBUTTONDOWN: 'WM_MBUTTONDOWN',
    win32con.WM_MBUTTONUP: 'WM_MBUTTONUP',
    win32con.WM_MOUSEWHEEL: 'WM_MOUSEWHEEL',
}

LPMSG = POINTER(MSG)

HOOKPROC = WINFUNCTYPE(LPARAM, c_int, WPARAM, LPARAM)


class MSLLHOOKSTRUCT(Structure):
    _fields_ = (('pt', POINT),
                ('mouseData', DWORD),
                ('flags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', WPARAM))


LPMSLLHOOKSTRUCT = POINTER(MSLLHOOKSTRUCT)


def errcheck_bool(result, func, args):
    if not result:
        raise WinError(get_last_error())
    return args


user32.SetWindowsHookExW.errcheck = errcheck_bool
user32.SetWindowsHookExW.restype = HHOOK
user32.SetWindowsHookExW.argtypes = (c_int,  # _In_ idHook
                                     HOOKPROC,  # _In_ lpfn
                                     HINSTANCE,  # _In_ hMod
                                     DWORD)  # _In_ dwThreadId

user32.CallNextHookEx.restype = LPARAM
user32.CallNextHookEx.argtypes = (HHOOK,  # _In_opt_ hhk
                                  c_int,  # _In_     nCode
                                  WPARAM,  # _In_     wParam
                                  LPARAM)  # _In_     lParam

user32.GetMessageW.argtypes = (LPMSG,  # _Out_    lpMsg
                               HWND,  # _In_opt_ hWnd
                               UINT,  # _In_     wMsgFilterMin
                               UINT)  # _In_     wMsgFilterMax

user32.TranslateMessage.argtypes = (LPMSG,)
user32.DispatchMessageW.argtypes = (LPMSG,)


@HOOKPROC
def LLMouseProc(nCode, wParam, lParam):
    msg = cast(lParam, LPMSLLHOOKSTRUCT)[0]
    if nCode == win32con.HC_ACTION:
        msgid = MSG_TEXT.get(wParam, str(wParam))
        msg = ((msg.pt.x, msg.pt.y),
               msg.mouseData, msg.flags,
               msg.time, msg.dwExtraInfo)
        print('{:15s}: {}'.format(msgid, msg))
    return user32.CallNextHookEx(None, nCode, wParam, lParam)


def mouse_msg_loop():
    hHook = user32.SetWindowsHookExW(win32con.WH_MOUSE_LL, LLMouseProc, None, 0)
    msg = MSG()
    while True:
        bRet = user32.GetMessageW(byref(msg), None, 0, 0)
        if not bRet:
            break
        if bRet == -1:
            raise WinError(get_last_error())
    user32.TranslateMessage(byref(msg))
    user32.DispatchMessageW(byref(msg))


if __name__ == '__main__':
    mouse_msg_loop()
