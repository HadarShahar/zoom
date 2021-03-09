"""
    Hadar Shahar
    OpeningWindow.
"""
import sys
import threading
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from GUI.gui_constants import *
from GUI.main_window import MainWindow
from client.auth.auth_client import AuthClient
from network.custom_messages.client_info import ClientInfo
from GUI.gui_constants import OPENING_WINDOW_UI_FILE_PATH, LOADING_GIF_PATH


class OpeningWindow(QtWidgets.QWidget):
    """ Definition of the class OpeningWindow. """

    def __init__(self):
        """ Constructor. """
        super(OpeningWindow, self).__init__()
        uic.loadUi(OPENING_WINDOW_UI_FILE_PATH, self)
        self.setWindowTitle("Hadar's Zoom")

        self.auth_client = AuthClient()
        self.auth_client.start()
        self.google_sign_in_button.clicked.connect(
            self.auth_client.google_sign_in)
        self.name_sign_in_button.clicked.connect(self.name_sign_in)
        self.no_name_error_label.hide()
        self.loading_frame.hide()

        # QLineEdit will emit the signal returnPressed()
        # whenever the user presses the enter key while in it
        self.name_input.returnPressed.connect(self.name_sign_in)

        # when the text in the name_input is edited, hide the no_name_error_label
        self.name_input.textEdited.connect(self.no_name_error_label.hide)
        # self.name_input.setFocus()

        self.loading_gif.setMovie(QtGui.QMovie(LOADING_GIF_PATH))
        self.main_window = MainWindow()
        self.main_window.finish_loading.connect(self.start_main_window)

        self.auth_client.recv_client_info_signal.connect(self.recv_client_info)
        self.auth_client.network_error.connect(self.handle_network_error)

    def name_sign_in(self):
        """ Authenticates the user using its name. """
        name = self.name_input.text()
        if name:
            threading.Thread(target=self.auth_client.name_sign_in,
                             args=(name,)).start()
            self.show_loading()
        else:
            self.no_name_error_label.show()

    def recv_client_info(self, client_info: ClientInfo):
        """
        This is a callback function which is called when the
        auth_client receives the client info from the sever.
        It sets up the main window.
        """
        print('received_client_info:', client_info)
        OpeningWindow.bring_win_to_front(self)
        self.show_loading()
        self.main_window.setup(client_info)
        # threading.Thread(target=self.main_window.start_clients).start()

    def show_loading(self):
        """ Shows the loading gif. """
        self.login_frame.hide()
        self.loading_frame.show()
        self.loading_gif.movie().start()

    def handle_network_error(self, details: str):
        """ Handles network error from the auth client. """
        self.loading_frame.hide()
        self.login_frame.show()
        self.main_window.handle_network_error(details)

    def start_main_window(self):
        """ Closes this window and start the main window. """
        self.close()
        self.main_window.show()
        OpeningWindow.bring_win_to_front(self.main_window)

    @staticmethod
    def bring_win_to_front(window):
        """
        Brings a given window to the front and acts like a "normal" window
        (can be underneath if another window is raised).
        """
        # set always on top flag, makes window disappear
        window.setWindowFlags(window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        window.show()  # makes window reappear, but it's ALWAYS on top

        # clear always on top flag, makes window disappear
        window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        window.show()  # makes window reappear, acts like normal window


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
