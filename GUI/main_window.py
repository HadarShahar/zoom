"""
    Hadar Shahar
    The main app code.
"""
from PyQt5 import QtWidgets, QtGui, uic
import numpy as np
import sys

# add the parent directory to the "module search path"
# in order to import files from other folders
sys.path.insert(0, '..')

from constants import *
from GUI.gui_constants import *

from GUI.controls_bar.controls_bar_frame import ControlsBarFrame
from GUI.video_grid.video_grid import VideoGrid
from GUI.chat.chat_window import ChatWindow
from GUI.smart_board.smart_board import SmartBoard
from GUI.widgets.basic_video_widget import BasicVideoWidget
from GUI.controls_bar.toggle_widget import ToggleWidget
from GUI.widgets.remote_window_container import RemoteWindowContainer

from client.info_client import InfoClient
from client.video.camera_client import CameraClient
from client.video.share_screen_client import ShareScreenClient
from client.audio.audio_client import AudioClient


# ========================================================== important!!!
# without it, PyQt5 immediately aborts when encountering
# an unhandled exception, without traceback
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# When an exception is raised and uncaught,the interpreter calls sys.excepthook
sys.excepthook = except_hook


class MainWindow(QtWidgets.QMainWindow):
    """ Definition of the class MainWindow. """
    UI_FILEPATH = 'ui_main_window.ui'

    def __init__(self):
        """ Initializes the main window. """
        super(MainWindow, self).__init__()

        self.is_audio_on = True
        self.is_video_on = True

        # temporary values
        self.id = b''
        self.name = ''
        self.clients = []
        self.init_clients()

        uic.loadUi(MainWindow.UI_FILEPATH, self)

        self.create_controls_bar()
        self.create_video_grid()
        self.create_chat_window()
        self.create_shared_screen()
        self.create_smart_board()
        self.init_remote_window()

    def init_clients(self):
        """ 
        Initializes the clients and starts them,
        each one in a different thread.
        """
        # ================================================= info
        self.info_client = InfoClient(SERVER_IP, CLIENT_IN_INFO_PORT,
                                      CLIENT_OUT_INFO_PORT)
        self.id = self.info_client.id
        self.name = self.info_client.name
        self.info_client.new_info.connect(self.handle_new_info)

        # ================================================= video
        self.video_client = CameraClient(SERVER_IP, CLIENT_IN_VIDEO_PORT,
                                         CLIENT_OUT_VIDEO_PORT, self.id)
        # # print(id(self.video_client.frame_captured))
        # # VideoClient.frame_captured.connect( # doesn't work
        # self.video_client.frame_captured.connect(self.video_grid.show_my_frame)
        # self.video_client.frame_received.connect(
        #     self.video_grid.show_video_frame)

        # ================================================= share screen
        self.share_screen_client = ShareScreenClient(
            SERVER_IP, CLIENT_IN_SCREEN_PORT, CLIENT_OUT_SCREEN_PORT, self.id)
        self.share_screen_client.frame_captured.connect(
            lambda frame: self.show_shared_screen(frame, self.id)
        )
        self.share_screen_client.frame_received.connect(
            self.show_shared_screen)

        # ================================================= audio
        self.audio_client = AudioClient(SERVER_IP, CLIENT_IN_AUDIO_PORT,
                                        CLIENT_OUT_AUDIO_PORT, self.id)

        # ================================================= start the clients
        # must be a list because chat client will be added
        self.clients = [self.info_client, self.video_client,
                        self.share_screen_client, self.audio_client]
        for client in self.clients:
            client.start()

    def handle_new_info(self, info: tuple):
        """
        Handles new information received from the InfoClient.
        """
        msg_name, msg_data = info

        if msg_name == Info.NEW_CLIENT:
            self.add_client(*msg_data)
        elif msg_name == Info.CLIENTS_INFO:
            # msg_data is a list ot tuples
            for tup in msg_data:
                self.add_client(*tup)

        # msg_data is the client id
        elif msg_name == Info.TOGGLE_AUDIO:
            self.video_grid.get_video_widget(msg_data).toggle_audio()
        elif msg_name == Info.TOGGLE_VIDEO:
            self.video_grid.get_video_widget(msg_data).toggle_video()

        elif msg_name == Info.CLIENT_LEFT:
            self.video_grid.remove_video_widget(msg_data)
            self.chat_window.remove_client(msg_data)
        elif msg_name == Info.NEW_PAINTING:
            self.smart_board.draw_painting(msg_data)
        elif msg_name == Info.REMOTE_WINDOW_MSG:
            self.remote_window_container.remote_window. \
                handle_new_msg(msg_data)

        widgets_start_msgs = {
            Info.START_SCREEN_SHARING: self.shared_screen,
            Info.START_PAINTING: self.smart_board,
            Info.START_REMOTE_WINDOW: self.remote_window_container
        }
        for start_msg, widget in widgets_start_msgs.items():
            if msg_name == start_msg:
                widget.show()
            elif msg_name == Info.OPPOSITE_MSGS[start_msg]:
                widget.hide()

    def create_controls_bar(self):
        """ Creates the controls bar. """
        self.controls_bar = ControlsBarFrame(
            self.main_frame, self.is_audio_on, self.is_video_on)
        self.main_grid_layout.addWidget(self.controls_bar,
                                        # row, column, row_span, column_span
                                        # 3, 0, 1, 3)
                                        1, 0)
        self.controls_bar.leave_button.clicked.connect(self.exit)
        self.connect_toggles()

    def connect_toggles(self):
        """
        Connects all the toggle buttons in the controls bar
        to their callback methods.
        """
        bar = self.controls_bar
        bar.toggle_audio_widget.clicked.connect(self.toggle_audio)
        bar.toggle_video_widget.clicked.connect(self.toggle_video)
        bar.toggle_chat_widget.clicked.connect(self.toggle_chat)
        bar.toggle_share_screen_widget.clicked.connect(
            self.toggle_share_screen)
        bar.toggle_smart_board_widget.clicked.connect(self.toggle_smart_board)
        bar.toggle_remote_window_widget.clicked.connect(
            self.toggle_remote_window)

    def toggle_audio(self):
        """ Turns on/off the audio. """
        self.audio_client.toggle_is_sharing()
        self.video_grid.get_video_widget(self.id).toggle_audio()
        self.info_client.send_toggle_msg(Info.TOGGLE_AUDIO)

    def toggle_video(self):
        """ Turns on/off the video. """
        self.video_client.toggle_is_sharing()
        self.video_grid.get_video_widget(self.id).toggle_video()
        self.info_client.send_toggle_msg(Info.TOGGLE_VIDEO)

    def toggle_chat(self):
        """ Shows/hides the chat. """
        if self.controls_bar.toggle_chat_widget.is_on:
            self.chat_window.show()
        else:
            self.chat_window.hide()

    def add_client(self, client_id: bytes, client_name: str,
                   is_audio_on: bool, is_video_on: bool):
        """ Adds a client to the gui. """
        self.video_grid.add_video_widget(
            client_id, client_name, is_audio_on, is_video_on)
        self.chat_window.add_client(client_id, client_name)

    def create_video_grid(self):
        """ Creates the video grid. """
        self.video_grid = VideoGrid(self.video_client,
                                    self.video_grid_container)
        self.video_grid.add_video_widget(self.id, self.name,
                                         is_audio_on=self.is_audio_on,
                                         is_video_on=self.is_video_on)

        self.video_grid_container_layout.addWidget(
            self.video_grid, 1, 1)  # 1, 1 because of the spacers

    def create_chat_window(self):
        """ Creates the chat window. """
        self.chat_window = ChatWindow(self.id, self.horizontal_splitter)
        self.clients.append(self.chat_window.client)

    def create_shared_screen(self):
        """ Creates the shared screen. """
        self.shared_screen = BasicVideoWidget(
            self.main_vertical_splitter)
        self.shared_screen.hide()

    def show_shared_screen(self, frame: np.ndarray, client_id: bytes):
        """ Shows a given frame in the shared screen. """
        # show the frame only if the shared screen is visible
        if self.shared_screen.isVisible():
            self.shared_screen.show_frame(frame)

    def create_smart_board(self):
        """ Creates the smart board. """
        self.smart_board = SmartBoard(self.main_vertical_splitter)
        self.smart_board.new_painting.connect(
            self.info_client.send_painting_msg)
        self.smart_board.hide()

    def init_remote_window(self):
        """ Initializes the remote window and creates its container. """
        # RemoteWindowContainer
        self.remote_window_container = \
            RemoteWindowContainer(self.main_vertical_splitter)
        self.remote_window_container.remote_window.new_msg.connect(
            self.info_client.send_remote_window_msg)
        self.remote_window_container.hide()

    def can_start_sharing(self) -> bool:
        """
        Checks if can start screen/smart_board/remote_window sharing -
        if none of the participants is already sharing.
        """
        # if one of these widgets is visible, someone is already sharing
        widgets = (self.shared_screen, self.smart_board,
                   self.remote_window_container)
        for widget in widgets:
            if widget.isVisible():
                self.show_error_msg("Can't start sharing",
                                    "A participant is already sharing.")
                return False
        return True

    def toggle_share_screen(self):
        """ Toggles the screen sharing. """
        toggled = self.toggle_sharing(
            self.controls_bar.toggle_share_screen_widget, self.shared_screen,
            Info.START_SCREEN_SHARING, Info.STOP_SCREEN_SHARING)
        if toggled:
            self.share_screen_client.toggle_is_sharing()

    def toggle_smart_board(self):
        """ Toggle the smart board sharing. """
        self.toggle_sharing(
            self.controls_bar.toggle_smart_board_widget, self.smart_board,
            Info.START_PAINTING, Info.STOP_PAINTING)

    def toggle_remote_window(self):
        """ Toggles the remote window. """
        self.toggle_sharing(
            self.controls_bar.toggle_remote_window_widget,
            self.remote_window_container,
            Info.START_REMOTE_WINDOW, Info.STOP_REMOTE_WINDOW)

    def toggle_sharing(self, toggle_widget: ToggleWidget,
                       ui_widget: QtWidgets.QWidget,
                       start_msg: int, stop_msg: int) -> bool:
        """
        Tries to toggle a widget that starts and stops sharing
        (screen sharing / smart board / remote window).
        If another sharing is currently live,
        one can't start a new one until the live sharing finishes.

        :param toggle_widget: The switch that turns on/off this sharing.
        :param ui_widget: The widget in the ui.
        :param start_msg: The info message to send when start sharing.
        :param stop_msg:  The info message to send when stop sharing.
        :param stop_msg:  The info message to send when stop sharing.
        :return: True if the toggle widget was toggled, False otherwise
        """
        if toggle_widget.is_on or self.can_start_sharing():
            if toggle_widget.is_on:
                self.info_client.send_info_msg((stop_msg, self.id))
                ui_widget.hide()
            else:
                self.info_client.send_info_msg((start_msg, self.id))
                ui_widget.show()
            toggle_widget.toggle()
            return True
        return False

    def moveEvent(self, event: QtGui.QMoveEvent):
        """
        This function is called when this window is moved.
        It updates the main_window_pos in the remote_window_container.
        """
        super(MainWindow, self).moveEvent(event)
        self.remote_window_container.set_main_window_pos(event.pos())

    def exit(self):
        """ Closes the clients and the gui. """
        for client in self.clients:
            client.close()
        self.close()  # close the gui

    @staticmethod
    def show_error_msg(text: str, info_text: str):
        """ Shows an error message with given text. """
        msg = QtWidgets.QMessageBox()
        msg.setIcon(
            QtWidgets.QMessageBox.Critical)  # QtWidgets.QMessageBox.Warning
        msg.setText(text)
        msg.setInformativeText(info_text)
        msg.setWindowTitle('Error')
        msg.exec_()


def main():
    """
    Creates the application and the main window,
    and starts the event loop.
    """
    # create the app and apply the style sheet to it
    app = QtWidgets.QApplication([])
    with open(STYLE_SHEET_PATH, 'r') as file:
        app.setStyleSheet(file.read())

    # create the main window
    win = MainWindow()
    win.show()

    # start the event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
