"""
    Hadar Shahar
    The main app code.
"""
from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import pyqtSignal
import socket
import sys

from network.custom_messages.client_info import ClientInfo
from network.custom_messages.general_info import Info
from GUI.gui_constants import *

from GUI.controls_bar.controls_bar_frame import ControlsBarFrame
from GUI.video_grid.video_grid import VideoGrid
from GUI.chat.chat_window import ChatWindow
from GUI.smart_board.smart_board import SmartBoard
from GUI.widgets.basic_video_widget import BasicVideoWidget
from GUI.controls_bar.toggle_widget import ToggleWidget
from GUI.widgets.remote_window_container import RemoteWindowContainer
from GUI.window_utils import bring_win_to_front, show_error_window, \
    confirm_quit_dialog

from client.info_client import InfoClient
from client.video.camera_client import CameraClient
from client.video.share_screen_client import ShareScreenClient
from client.audio.audio_client import AudioClient


class MainWindow(QtWidgets.QMainWindow):
    """ Definition of the class MainWindow. """
    finish_loading = pyqtSignal()

    # this signal is emitted when this window is closed
    exit_signal = pyqtSignal()

    def __init__(self):
        """ Initializes the main window. """
        super(MainWindow, self).__init__()
        uic.loadUi(MAIN_WINDOW_UI_FILE_PATH, self)
        self.clients = []
        self.running = True

    def setup(self, client_info: ClientInfo) -> bool:
        """
         Sets up the clients and the gui objects.
         :returns: True if the set up was successful, False otherwise.
         """
        self.client_info = client_info
        self.setWindowTitle(f'Meeting ID:   {self.format_meeting_id()}')
        if not self.init_clients():
            return False

        self.create_controls_bar()
        self.create_video_grid()
        self.create_chat_window()
        self.create_shared_screen()
        self.create_smart_board()
        self.init_remote_window()

        # after the clients and all the gui objects have been created,
        # connect the clients' signals to the gui objects
        self.connect_clients()

        # def start_clients(self):
        for client in self.clients:
            client.start()

        print('finish_loading')
        self.finish_loading.emit()
        return True

    def format_meeting_id(self, letters_group_size=3, separator=' ') -> str:
        """
        :param letters_group_size: how many letters to group together.
        :param separator: the separator between the letters groups.
        :returns: the formatted string.
        """
        st = self.client_info.meeting_id.hex()
        n = letters_group_size
        return separator.join([st[i: i + n] for i in range(0, len(st), n)])

    def init_clients(self) -> bool:
        """
        Initializes the clients.
        :returns: True if in initialization was successful, False otherwise.
        """
        try:
            self.info_client = InfoClient(self.client_info)
            self.video_client = CameraClient(self.client_info.id)
            self.share_screen_client = ShareScreenClient(self.client_info.id)
            self.audio_client = AudioClient(self.client_info.id)

            # must be a list because chat client will be added
            self.clients += [self.info_client, self.video_client,
                             self.share_screen_client, self.audio_client]
            return True
        except socket.error as e:
            self.handle_network_error(str(e))
        return False

    def connect_clients(self):
        """ Connects the clients' signals to the corresponding functions. """
        self.info_client.new_info.connect(self.handle_new_info)
        self.share_screen_client.frame_captured.connect(
            lambda frame: self.show_shared_screen(frame, self.client_info.id)
        )
        self.share_screen_client.frame_received.connect(
            self.show_shared_screen)
        for client in self.clients:
            client.network_error.connect(self.handle_network_error)

    def handle_new_info(self, info: tuple):
        """
        Handles new information received from the InfoClient.
        """
        msg_name, msg_data = info

        if msg_name == Info.NEW_CLIENT:
            self.add_client(msg_data)
        elif msg_name == Info.CLIENTS_INFO:
            # msg_data is a list ot ClientInfo objects
            for client_info in msg_data:
                self.add_client(client_info)

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
            self.main_frame, self.client_info.is_audio_on,
            self.client_info.is_video_on)
        self.main_grid_layout.addWidget(self.controls_bar)
        # self.main_grid_layout.addWidget(self.controls_bar, 1, 0) #row, column
        self.controls_bar.leave_button.clicked.connect(self.confirm_exit)
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
        self.video_grid.get_video_widget(self.client_info.id).toggle_audio()
        self.info_client.send_toggle_msg(Info.TOGGLE_AUDIO)

    def toggle_video(self):
        """ Turns on/off the video. """
        self.video_client.toggle_is_sharing()
        self.video_grid.get_video_widget(self.client_info.id).toggle_video()
        self.info_client.send_toggle_msg(Info.TOGGLE_VIDEO)

    def toggle_chat(self):
        """ Shows/hides the chat. """
        if self.controls_bar.toggle_chat_widget.is_on:
            self.chat_window.show()
        else:
            self.chat_window.hide()

    def add_client(self, client_info: ClientInfo):
        """ Adds a client to the gui. """
        self.video_grid.add_video_widget(client_info)
        self.chat_window.add_client(client_info.id, client_info.name)

    def create_video_grid(self):
        """ Creates the video grid. """
        self.video_grid = VideoGrid(self.video_client,
                                    self.video_grid_container)
        self.video_grid.add_video_widget(self.client_info)

        self.video_grid_container_layout.addWidget(self.video_grid,
                                                   *VIDEO_GRID_POSITION)

    def create_chat_window(self):
        """ Creates the chat window. """
        self.chat_window = ChatWindow(self.client_info.id,
                                      self.horizontal_splitter)
        self.clients.append(self.chat_window.client)

    def create_shared_screen(self):
        """ Creates the shared screen. """
        self.shared_screen = BasicVideoWidget(
            self.main_vertical_splitter)
        self.shared_screen.hide()

    def show_shared_screen(self, frame, client_id: bytes):
        """
        Shows a given frame in the shared screen.
        :param frame: a frame of the shared screen (numpy array).
        :param client_id: the id of the client who sent it.
        """
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
                show_error_window("Can't start sharing",
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
        :return: True if the toggle widget was toggled, False otherwise
        """
        if toggle_widget.is_on or self.can_start_sharing():
            if toggle_widget.is_on:
                self.info_client.send_info_msg((stop_msg, self.client_info.id))
                ui_widget.hide()
            else:
                self.info_client.send_info_msg(
                    (start_msg, self.client_info.id))
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

    def handle_network_error(self, details: str):
        """
        Handles a network error from the clients -
        displays an error message and exits.
        """
        if self.running:
            self.running = False
            if self.isVisible():
                bring_win_to_front(self)
            show_error_window('Network error', details)
            self.exit()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """ This function is called when this window is closed. """
        if self.running:
            if not self.confirm_exit():
                event.ignore()
        else:
            event.accept()

    def confirm_exit(self) -> bool:
        """
        Asks the client if it wants to exit and exits if it confirms.
        :returns: True if it has exited, False otherwise.
        """
        confirm_dialog_text = 'Are you sure you want to leave the meeting?'
        if not confirm_quit_dialog(confirm_dialog_text):
            return False
        self.exit()
        return True

    def exit(self):
        """ Closes the clients and the gui. """
        self.running = False
        self.exit_signal.emit()
        for client in self.clients:
            client.close()
        self.close()  # close the gui


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
    if not win.setup(ClientInfo(b'100', b'200', 'TestUser')):
        return
    win.show()

    # start the event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
