"""
    Hadar Shahar
    OpeningWindow.
"""
import sys
import threading
from PyQt5 import QtWidgets, uic, QtGui
from GUI.gui_constants import *
from GUI.main_window import MainWindow
from client.auth.auth_client import AuthClient
from network.custom_messages.client_info import ClientInfo
from GUI.gui_constants import OPENING_WINDOW_UI_FILE_PATH, LOADING_GIF_PATH
from GUI.window_utils import bring_win_to_front, show_error_window


def except_hook(cls, exception, traceback):
    """
    Global exception handler.
    Without it, PyQt5 immediately aborts when encountering
    an unhandled exception, without traceback.
    """
    sys.__excepthook__(cls, exception, traceback)


# When an exception is raised and uncaught,the interpreter calls sys.excepthook
sys.excepthook = except_hook


class OpeningWindow(QtWidgets.QWidget):
    """ Definition of the class OpeningWindow. """

    WINDOW_HEIGHT = 420

    def __init__(self):
        """ Constructor. """
        super(OpeningWindow, self).__init__()
        uic.loadUi(OPENING_WINDOW_UI_FILE_PATH, self)
        self.setWindowTitle(self.title_label.text())
        self.error_label.hide()
        self.join_meeting_frame.hide()
        self.loading_frame.hide()
        self.setFixedHeight(OpeningWindow.WINDOW_HEIGHT)

        self.auth_client = AuthClient()
        self.auth_client.start()

        self.main_window = None
        self.init_main_window()

        self.connect_signals()

    def init_main_window(self):
        """ Initializes the main window. """
        self.main_window = MainWindow()
        self.main_window.finish_loading.connect(self.start_main_window)
        self.main_window.exit_signal.connect(self.main_window_closed)

    def connect_signals(self):
        """ Connect the signals to their callback functions. """
        self.google_sign_in_button.clicked.connect(
            self.auth_client.google_sign_in)
        # QLineEdit will emit the signal returnPressed()
        # whenever the user presses the enter key while in it
        self.name_input.returnPressed.connect(self.name_sign_in)
        self.name_sign_in_button.clicked.connect(self.name_sign_in)
        self.name_input.textEdited.connect(self.error_label.hide)

        self.new_meeting_button.clicked.connect(self.new_meeting)
        self.meeting_id_input.returnPressed.connect(self.join_meeting)
        self.join_meeting_button.clicked.connect(self.join_meeting)
        self.meeting_id_input.textEdited.connect(self.error_label.hide)

        self.auth_client.recv_client_info_signal.connect(self.recv_client_info)
        self.auth_client.network_error.connect(self.handle_network_error)
        self.auth_client.invalid_id_error.connect(self.handle_invalid_id_error)

    def name_sign_in(self):
        """ Authenticates the user using its name. """
        name = self.name_input.text()
        if name:
            threading.Thread(target=self.auth_client.name_sign_in,
                             args=(name,)).start()
            self.show_loading()
        else:
            self.error_label.setText('You must enter a name.')
            self.error_label.show()

    def recv_client_info(self, client_info: ClientInfo):
        """
        This is a callback function which is called when the
        auth_client receives the client info from the sever.
        It shows the join_meeting_frame if the client has just signed in,
        or starts the main window (meeting window)
        if client has created / joined a meeting.
        """
        print('received_client_info:', client_info)
        bring_win_to_front(self)
        self.loading_frame.hide()
        self.login_frame.hide()

        if client_info.meeting_id:
            self.meeting_id_input.clear()
            self.show_loading()
            self.main_window.setup(client_info)
            # threading.Thread(target=self.main_window.start_clients).start()
        else:
            self.join_meeting_frame.show()
            self.title_label.setText(f'Welcome {client_info.name}!')

    def show_loading(self):
        """ Hides the frames and shows the loading gif. """
        self.login_frame.hide()
        self.join_meeting_frame.hide()
        self.loading_gif.setMovie(QtGui.QMovie(LOADING_GIF_PATH))
        self.loading_gif.movie().start()
        self.loading_frame.show()

    def new_meeting(self):
        """
        Starts a thread that sends a request to create a new meeting.
        """
        threading.Thread(target=self.auth_client.new_meeting).start()
        self.show_loading()

    def join_meeting(self):
        """
        Starts a thread that sends a request to join a meeting
        with the id entered in meeting_id_input.
        """
        meeting_id = self.meeting_id_input.text().replace(' ', '')
        if meeting_id:
            threading.Thread(target=self.auth_client.join_meeting,
                             args=(meeting_id,)).start()
            self.show_loading()
        else:
            self.error_label.setText('You must enter a meeting ID.')
            self.error_label.show()

    def handle_network_error(self, details: str):
        """ Handles network error from the auth client. """
        self.loading_frame.hide()
        self.login_frame.show()
        bring_win_to_front(self)
        show_error_window('Network error', details)

    def handle_invalid_id_error(self, details: str):
        """ Handles invalid id error from the auth client. """
        self.loading_frame.hide()
        self.join_meeting_frame.show()
        bring_win_to_front(self)
        show_error_window(details, '')

    def start_main_window(self):
        """ Closes this window and start the main window. """
        self.loading_frame.hide()
        self.join_meeting_frame.show()
        self.hide()
        self.main_window.show()
        bring_win_to_front(self.main_window)

    def main_window_closed(self):
        """ This function is called when the main window is closed. """
        self.show()
        # initializes a new main window, if the client will join a new meeting
        self.init_main_window()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        This function is called when this window is closed.
        It logs the user out.
        """
        self.auth_client.logout()


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
