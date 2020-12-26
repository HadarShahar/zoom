"""
    Hadar Shahar
    RemoteNotepad.
"""
import ctypes
import time
import datetime
import struct
import win32gui
from win32con import *
from ctypes.wintypes import DWORD
from PyQt5.QtCore import pyqtSignal, QMutex

from win32.remote_window import RemoteWindow
from win32.notepad_state import NotepadState
from remote_window_msg import RemoteWindowMsg

user32 = ctypes.WinDLL('User32.dll')


# user32 = ctypes.windll.user32


class RemoteNotepad(RemoteWindow):
    """
    Definition of the class RemoteNotepad.
    It represents a notepad window, that is shared with remote clients.
    """

    PROGRAM_NAME = 'notepad.exe'
    EDIT_CLASS_NAME = 'Edit'  # the class name of the child window, the editor

    # PROGRAM_NAME = r'C:\Program Files\Notepad++\notepad++.exe'
    # EDIT_CLASS_NAME = 'Scintilla'
    # PROGRAM_NAME = r'C:\Users\user\AppData\Local\Programs' \
    #                r'\Microsoft VS Code\Code.exe'
    # EDIT_CLASS_NAME = 'Chrome_WidgetWin_1'

    # if the difference in the text length is greater than this threshold,
    # send all the text to sync the editors.
    LEN_DIFF_THRESHOLD = 10
    LINE_SEPARATOR = '\r\n'
    LOOP_DELAY_TIME = 0.25

    new_msg = pyqtSignal(RemoteWindowMsg)

    def __init__(self):
        """ Constructor. """
        super(RemoteNotepad, self).__init__(RemoteNotepad.PROGRAM_NAME)
        self.hwnd_edit = None
        self.last_state = NotepadState()
        self.mutex = QMutex()

    def create_window(self):
        """
        Creates the window and gets a handle to it (in the parent constructor),
        and a handle to its child window, the editor.
        """
        super(RemoteNotepad, self).create_window()
        self.hwnd_edit = win32gui.FindWindowEx(
            self.hwnd, None, RemoteNotepad.EDIT_CLASS_NAME, None)
        print('hwnd_edit:', self.hwnd_edit)

    def run(self):
        """
        The main loop of the remote notepad.
        It sends messages using the new_msg signal whenever
        the text in the edit control changes.
        """
        try:
            while self.is_open:
                # self.time_demo()
                time.sleep(RemoteNotepad.LOOP_DELAY_TIME)

                if self.check_lines_diff() or self.check_text_len_diff():
                    continue

                start_pos, end_pos = selection = self.get_selection()
                if start_pos != end_pos:  # if there's a selection of text
                    if selection != self.last_state.selection:
                        msg = RemoteWindowMsg(RemoteWindowMsg.SET_SELECTION,
                                              (start_pos, end_pos))
                        self.new_msg.emit(msg)
                else:
                    if self.was_text_modified():
                        # A value of -1 specifies the current line number
                        current_line = self.line_from_char_index(-1)
                        data = (self.get_line_index(-1), current_line)
                        msg = RemoteWindowMsg(RemoteWindowMsg.REPLACE_LINE,
                                              data)
                        self.new_msg.emit(msg)

                self.last_state.selection = selection
        except Exception as e:
            print('RemoteNotepad.run:', e)
            self.close()

    def check_lines_diff(self) -> bool:
        """
        Checks if the number of lines has changed since the last check,
        and sends all the text if it has.
        """
        lines_count = self.count_lines()
        if lines_count == self.last_state.lines_count:
            return False
        self.send_all_text()
        self.last_state.lines_count = lines_count
        return True

    def check_text_len_diff(self) -> bool:
        """
        Checks if the difference in the text length is greater than the
        threshold, and if it is, sends all the text to sync the editors.
        """
        current_text = self.get_text()
        diff = abs(len(current_text) - self.last_state.text_len)
        if diff <= RemoteNotepad.LEN_DIFF_THRESHOLD:
            return False
        print('check_text_len_diff:', diff)
        self.send_all_text(current_text)
        self.last_state.text_len = len(current_text)
        return True

    def send_all_text(self, current_text=''):
        """ Sends all the text. """
        if current_text == '':
            current_text = self.get_text()
        msg = RemoteWindowMsg(RemoteWindowMsg.SET_TEXT,
                              (current_text,))
        self.new_msg.emit(msg)

    def handle_new_msg(self, msg: RemoteWindowMsg):
        """ Handles new RemoteWindowMsg. """
        change_text_operations = {
            RemoteWindowMsg.REPLACE_LINE: self.replace_line,
            RemoteWindowMsg.SET_TEXT: self.set_text
        }
        if msg.type == RemoteWindowMsg.SET_SELECTION:
            self.set_selection(*msg.data)
            self.last_state.selection = msg.data
        elif msg.type in change_text_operations:
            # get the modification flag before the replacement
            # and restore it after (avoid infinite loop)
            modified = self.get_modify_flag()
            # save the current selection and restore it after
            selection = self.get_selection()

            func = change_text_operations[msg.type]
            func(*msg.data)

            self.set_selection(*selection)
            self.set_modify_flag(modified)

    def time_demo(self):
        """
        Just for testing.
        Replaces the first line (index 0) with the current time.
        """
        self.replace_line(0, str(datetime.datetime.now()))

    def get_line_length(self, char_index: int) -> int:
        """
        Returns the length of the line that contains
        the given character index.
        """
        return self.msg_to_edit_control(EM_LINELENGTH, char_index, 0)

    def get_line_index(self, char_index: int) -> int:
        """
        Returns the index of the line that contains
        the given character index (-1 for the current line).
        """
        return self.msg_to_edit_control(EM_LINEFROMCHAR, char_index, 0)

    def line_from_char_index(self, char_index: int) -> str:
        """
        Returns the line that contains the given character index.
        """
        line_index = self.get_line_index(char_index)
        line_length = self.get_line_length(char_index)
        if line_length == 0:
            return ''

        # Win32 API returns a UTF-16 string, each character is 16-bits
        buf_size = line_length * 2  # 16 bits = 2 bytes, so multiply by 2

        buffer = win32gui.PyMakeBuffer(buf_size)
        # Before sending the message EM_GETLINE,
        # the first word of the buffer should be its size (in TCHARs)
        # 'H' => unsigned short = 2 bytes
        buffer[:2] = struct.pack('H', buf_size)

        self.msg_to_edit_control(EM_GETLINE, line_index, buffer)
        return buffer.tobytes().decode('UTF-16')

    def count_lines(self) -> int:
        """ Returns the number of lines in the edit control. """
        return self.msg_to_edit_control(EM_GETLINECOUNT, 0, 0)

    def first_char_index(self, line_index: int) -> int:
        """ Returns the index of the first character in a given line. """
        return self.msg_to_edit_control(EM_LINEINDEX, line_index, 0)

    def replace_line(self, line_index: int, text: str):
        """
        Replaces the line in a given index (-1 for the current line)
        with a given text - selects the line, replaces it
        and restores the current selection in the end.
        """
        # save the current selection, to restore it in the end
        current_selection = self.get_selection()

        num_of_lines = self.count_lines()
        # line_index is zero based
        if line_index + 1 > num_of_lines:
            last_line_beginning = self.first_char_index(num_of_lines - 1)
            last_line_length = self.get_line_length(last_line_beginning)
            last_char_index = last_line_beginning + last_line_length
            # insert empty lines at the last char index
            self.set_selection(last_char_index, last_char_index)
            empty_lines = RemoteNotepad.LINE_SEPARATOR * \
                          (line_index + 1 - num_of_lines)
            self.msg_to_edit_control(EM_REPLACESEL, 0, empty_lines)

        line_beginning = self.first_char_index(line_index)
        line_length = self.get_line_length(line_beginning)

        self.set_selection(line_beginning, (line_beginning + line_length))
        self.msg_to_edit_control(EM_REPLACESEL, 0, text)

        # restore the selection
        self.set_selection(*current_selection)

    def get_text(self) -> str:
        """ Returns the text in the edit control. """
        text_length = self.msg_to_edit_control(WM_GETTEXTLENGTH, 0, 0)
        # Win32 API returns a UTF-16 string, each character is 16-bits
        buf_size = text_length * 2  # 16 bits = 2 bytes, so multiply by 2

        # buffer = ctypes.create_string_buffer(buf_size)
        # user32.SendMessageW(self.hwnd_edit, WM_GETTEXT, buf_size, buffer)
        # return buffer.raw.decode('UTF-16')

        buffer = win32gui.PyMakeBuffer(buf_size)
        self.msg_to_edit_control(WM_GETTEXT, buf_size, buffer)
        return buffer.tobytes().decode('UTF-16')

    def set_text(self, text: str):
        """ Sets the text in the edit control. """
        self.msg_to_edit_control(WM_SETTEXT, 0, text)
        self.last_state.text_len = len(text)
        self.last_state.lines_count = self.count_lines()

    def was_text_modified(self) -> bool:
        """
        Returns True if the text in the edit control
        was modified since the last check, False otherwise.
        """
        was_modified = self.get_modify_flag()
        self.set_modify_flag(False)  # clear the modification flag
        return was_modified

    def get_modify_flag(self) -> bool:
        """
        Gets the state of the edit control's modification flag - it indicates
        whether the text within the edit control has been modified.
        If it has been, the return value is nonzero; otherwise, it is zero.
        """
        was_modified = self.msg_to_edit_control(EM_GETMODIFY, 0, 0)
        return bool(was_modified)

    def set_modify_flag(self, value: bool):
        """ Sets the edit control's modification flag. """
        self.msg_to_edit_control(EM_SETMODIFY, value, 0)

    def get_selection(self) -> (int, int):
        """
        Returns the starting and the ending characters positions
        of the current selection.
        """
        start_pos = DWORD()
        end_pos = DWORD()
        self.mutex.lock()
        # TODO change this call
        user32.SendMessageW(self.hwnd_edit, EM_GETSEL,
                            ctypes.byref(start_pos), ctypes.byref(end_pos))
        self.mutex.unlock()
        return start_pos.value, end_pos.value

    def set_selection(self, start_pos: int, end_pos: int):
        """
        Sets the selection.
        :param start_pos: The starting character position of the selection.
        :param end_pos: The ending character position of the selection.
        """
        self.msg_to_edit_control(EM_SETSEL, start_pos, end_pos)

    def msg_to_edit_control(self, msg: int, wparam, lparam):
        """
        Sends a given message to the edit control with the given params,
        and returns the result of the SendMessage function.
        """
        if not self.mutex.tryLock():
            print('Could not acquire mutex')
            return 0
        # self.mutex.lock()
        ret = win32gui.SendMessage(self.hwnd_edit, msg, wparam, lparam)
        self.mutex.unlock()
        return ret


def main():
    notepad = RemoteNotepad()
    notepad.create_window()
    notepad.run()


if __name__ == '__main__':
    main()
