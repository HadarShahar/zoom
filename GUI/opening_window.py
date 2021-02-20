"""
    Hadar Shahar
    OpeningWindow.
"""
import sys
import threading
from PyQt5 import QtWidgets, uic
from GUI.gui_constants import *
from GUI.main_window import MainWindow
from constants import SERVER_IP, AUTH_SERVER_PORT
from client.auth.auth_client import AuthClient
from custom_messages.client_info import ClientInfo


class OpeningWindow(QtWidgets.QWidget):
    """ Definition of the class OpeningWindow. """
    UI_FILEPATH = 'ui_opening_window.ui'

    def __init__(self):
        super(OpeningWindow, self).__init__()
        uic.loadUi(OpeningWindow.UI_FILEPATH, self)

        self.auth_client = AuthClient(SERVER_IP, AUTH_SERVER_PORT)
        self.auth_client.start()
        self.google_sign_in_button.clicked.connect(
            self.auth_client.google_sign_in)
        self.sign_in_button.clicked.connect(self.name_sign_in)

        # QLineEdit will emit the signal returnPressed()
        # whenever the user presses the enter key while in it
        self.name_input.returnPressed.connect(self.name_sign_in)
        self.name_input.setFocus()

        self.auth_client.recv_client_info_signal.connect(self.recv_client_info)
        self.main_window = MainWindow()
        self.main_window.finish_loading.connect(self.start_main_window)

    def name_sign_in(self):
        name = self.name_input.text()
        if name:
            self.auth_client.name_sign_in(name)

    def recv_client_info(self, client_info: ClientInfo):
        print('received_client_info:', client_info)
        # TODO loading animation
        # threading.Thread(target=self.main_window.setup,
        #                  args=(client_info,)).start()
        self.main_window.setup(client_info)

    def start_main_window(self):
        self.close()
        self.main_window.show()


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
