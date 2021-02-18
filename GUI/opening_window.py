"""
    Hadar Shahar
    OpeningWindow.
"""
import sys
from PyQt5 import QtWidgets, QtGui, uic
from GUI.gui_constants import *
from GUI.main_window import MainWindow
from constants import SERVER_IP, AUTH_SERVER_PORT
from client.auth_client import AuthClient


class OpeningWindow(QtWidgets.QWidget):
    """ Definition of the class OpeningWindow. """
    UI_FILEPATH = 'ui_opening_window.ui'

    def __init__(self):
        super(OpeningWindow, self).__init__()
        uic.loadUi(OpeningWindow.UI_FILEPATH, self)

        self.auth_client = AuthClient(SERVER_IP, AUTH_SERVER_PORT,
                                      self.received_user_info)
        self.auth_client.start()
        self.google_sign_in_button.clicked.connect(
            self.auth_client.google_sign_in)

    def received_user_info(self, user_info: dict):
        print('*'*20, user_info)
        self.auth_client.close()
        # win = MainWindow()
        # win.show()
        # self.close()


def main():
    """
    Creates the application and the opening window,
    and starts the event loop.
    """
    # create the app and apply the style sheet to it
    app = QtWidgets.QApplication([])
    with open(STYLE_SHEET_PATH, 'r') as file:
        app.setStyleSheet(file.read())

    win = OpeningWindow()
    win.show()

    # start the event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
