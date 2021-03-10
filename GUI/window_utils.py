"""
    Hadar Shahar
    window utils.
"""
from PyQt5 import QtWidgets, QtCore


def bring_win_to_front(window):
    """
    Brings a given PyQt5 window to the front and acts like a "normal" window
    (can be underneath if another window is raised).
    """
    # set always on top flag, makes window disappear
    window.setWindowFlags(
        window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    window.show()  # makes window reappear, but it's ALWAYS on top

    # clear always on top flag, makes window disappear
    window.setWindowFlags(
        window.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
    window.show()  # makes window reappear, acts like normal window


def show_error_window(text: str, info_text: str):
    """ Shows an error window with given text. """
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(text)
    msg.setInformativeText(info_text)
    msg.setWindowTitle('Error')
    msg.exec_()
