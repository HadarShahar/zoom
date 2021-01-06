"""
    Hadar Shahar
    The main app code.
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
import numpy as np
import sys
import threading

# add the parent directory to the "module search path"
# in order to import files from other folders
sys.path.insert(0, '..')

from constants import *
from GUI.gui_constants import *

from GUI.ui_main_window import Ui_MainWindow
from GUI.widgets.video_grid import VideoGrid
from GUI.widgets.smart_board import SmartBoard
from GUI.widgets.basic_video_widget import BasicVideoWidget
from GUI.widgets.client_video_widget import ClientVideoWidget
from GUI.controls_bar.toggle_widget import ToggleWidget
from GUI.chat.msg_widget import MsgWidget
from GUI.widgets.remote_window_container import RemoteWindowContainer
from GUI.chat.chat_recipients import ChatRecipients

from client.info_client import InfoClient
from client.video.video_client import VideoClient
from client.video.share_screen_client import ShareScreenClient
from client.chat_client import ChatClient

from chat_msg import ChatMsg


# ========================================================== important!!!
# without it, PyQt5 immediately aborts when encountering
# an unhandled exception, without traceback
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# When an exception is raised and uncaught,the interpreter calls sys.excepthook
sys.excepthook = except_hook


# ======================================================================


class MainWindow(QtWidgets.QMainWindow):
    """ Definition of the class MainWindow. """

    def __init__(self):
        """ Initializes the main window. """
        super(MainWindow, self).__init__()

        self.is_audio_on = False  # just for testing
        self.is_video_on = True

        self.init_clients()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.create_controls_bar()
        self.create_video_grid()
        self.init_chat()
        self.create_shared_screen()
        self.create_smart_board()
        self.init_remote_window()

        # {client_id: ClientVideoWidget(...)}
        self.video_widgets: [bytes, ClientVideoWidget] = {}
        self.add_video_widget(self.id, self.name,
                              is_audio_on=self.is_audio_on,
                              is_video_on=self.is_video_on)

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
        self.video_client = VideoClient(SERVER_IP, CLIENT_IN_VIDEO_PORT,
                                        CLIENT_OUT_VIDEO_PORT, self.id)
        # print(id(self.video_client.frame_captured))
        # VideoClient.frame_captured.connect( # doesn't work
        self.video_client.frame_captured.connect(
            lambda frame: self.show_video_frame(frame, self.id)
        )
        self.video_client.frame_received.connect(self.show_video_frame)

        # ================================================= share screen
        self.share_screen_client = \
            ShareScreenClient(SERVER_IP, CLIENT_IN_SCREEN_PORT,
                              CLIENT_OUT_SCREEN_PORT, self.id)
        self.share_screen_client.frame_captured.connect(
            lambda frame: self.show_shared_screen(frame, self.id)
        )
        self.share_screen_client.frame_received.connect(
            self.show_shared_screen)

        # ================================================= audio
        # TODO uncomment!!!
        # self.audio_client = AudioClient(SERVER_IP, CLIENT_IN_AUDIO_PORT,
        #                                 CLIENT_OUT_AUDIO_PORT, self.id)

        # ================================================= chat
        self.chat_client = ChatClient(SERVER_IP, CLIENT_IN_CHAT_PORT,
                                      CLIENT_OUT_CHAT_PORT, self.id)
        self.chat_client.new_msg.connect(self.show_chat_msg)

        # ================================================= start the clients
        self.clients = (self.info_client, self.video_client,
                        self.share_screen_client,
                        # self.audio_client,  # TODO uncomment!!!
                        self.chat_client)
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
            self.video_widgets[msg_data].toggle_audio()
        elif msg_name == Info.TOGGLE_VIDEO:
            self.video_widgets[msg_data].toggle_video()

        elif msg_name == Info.CLIENT_LEFT:
            self.remove_video_widget(msg_data)
            self.chat_recipients.remove(msg_data)
        elif msg_name == Info.NEW_PAINTING:
            self.ui.smart_board.draw_painting(msg_data)
        elif msg_name == Info.REMOTE_WINDOW_MSG:
            self.ui.remote_window_container.remote_window. \
                handle_new_msg(msg_data)

        widgets_start_msgs = {
            Info.START_SCREEN_SHARING: self.ui.shared_screen,
            Info.START_PAINTING: self.ui.smart_board,
            Info.START_REMOTE_WINDOW: self.ui.remote_window_container
        }
        for start_msg, widget in widgets_start_msgs.items():
            if msg_name == start_msg:
                widget.show()
            elif msg_name == Info.OPPOSITE_MSGS[start_msg]:
                widget.hide()

    def create_controls_bar(self):
        """ Creates the controls bar. """
        self.ui.controls_bar = QtWidgets.QFrame(self.ui.main_frame)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Preferred)
        self.ui.controls_bar.setSizePolicy(size_policy)
        self.ui.controls_bar.setFixedHeight(55)
        self.ui.controls_bar.setObjectName('chat')

        self.ui.controls_bar_layout = \
            QtWidgets.QHBoxLayout(self.ui.controls_bar)
        self.ui.controls_bar_layout. \
            setContentsMargins(0, 0, 10, 0)  # left, top, right, bottom
        self.ui.controls_bar_layout.setSpacing(0)

        self.create_toggles()

        self.ui.controls_bar_layout.addItem(self.default_hspacer())

        self.ui.leave_button = QtWidgets.QPushButton('Leave',
                                                     self.ui.controls_bar)
        self.ui.leave_button.setFixedSize(QtCore.QSize(60, 25))
        self.ui.leave_button.setObjectName('leave_button')
        self.ui.leave_button.clicked.connect(self.exit)
        self.ui.controls_bar_layout.addWidget(self.ui.leave_button)

        self.ui.main_grid_layout.addWidget(self.ui.controls_bar,
                                           # row, column, row_span, column_span
                                           # 3, 0, 1, 3)
                                           1, 0)

    def create_toggles(self):
        """
        Creates the toggle widgets for
        audio, video, chat, share screen, smart board and remote window.
        """
        self.ui.toggle_audio_widget = \
            ToggleWidget(self.ui.controls_bar, TOGGLE_AUDIO_DICT,
                         is_on=self.is_audio_on)
        self.ui.toggle_audio_widget.clicked.connect(self.toggle_audio)

        self.ui.toggle_video_widget = \
            ToggleWidget(self.ui.controls_bar, TOGGLE_VIDEO_DICT,
                         is_on=self.is_video_on)
        self.ui.toggle_video_widget.clicked.connect(self.toggle_video)

        self.ui.toggle_chat_widget = \
            ToggleWidget(self.ui.controls_bar, TOGGLE_CHAT_DICT, is_on=False)
        self.ui.toggle_chat_widget.clicked.connect(self.toggle_chat)

        self.ui.toggle_share_screen_widget = \
            ToggleWidget(self.ui.controls_bar, TOGGLE_SHARE_SCREEN_DICT,
                         is_on=False, toggle_onclick=False)
        self.ui.toggle_share_screen_widget. \
            clicked.connect(self.toggle_share_screen)

        self.ui.toggle_smart_board_widget = \
            ToggleWidget(self.ui.controls_bar, TOGGLE_SMART_BOARD_DICT,
                         is_on=False, toggle_onclick=False)
        self.ui.toggle_smart_board_widget.clicked. \
            connect(self.toggle_smart_board)

        self.ui.toggle_remote_window_widget = \
            ToggleWidget(self.ui.controls_bar, TOGGLE_REMOTE_WINDOW_DICT,
                         is_on=False, toggle_onclick=False)
        self.ui.toggle_remote_window_widget.clicked. \
            connect(self.toggle_remote_window)

        # add all the toggle widgets to the controls bar layout
        widgets = (self.ui.toggle_audio_widget,
                   self.ui.toggle_video_widget,
                   self.ui.toggle_chat_widget,
                   self.ui.toggle_share_screen_widget,
                   self.ui.toggle_smart_board_widget,
                   self.ui.toggle_remote_window_widget)
        for widget in widgets:
            self.ui.controls_bar_layout.addWidget(widget)

    def toggle_audio(self):
        """ Turns on/off the audio. """
        self.audio_client.toggle_is_sharing()
        self.video_widgets[self.id].toggle_audio()
        self.info_client.send_toggle_msg(Info.TOGGLE_AUDIO)

    def toggle_video(self):
        """ Turns on/off the video. """
        self.video_client.toggle_is_sharing()
        self.video_widgets[self.id].toggle_video()
        self.info_client.send_toggle_msg(Info.TOGGLE_VIDEO)

    def toggle_chat(self):
        """ Shows/hides the chat. """
        if self.ui.toggle_chat_widget.is_on:
            self.ui.chat_frame.show()
        else:
            self.ui.chat_frame.hide()

    def add_client(self, client_id: bytes, client_name: str,
                   is_audio_on: bool, is_video_on: bool):
        """ Adds a client to the gui. """
        self.add_video_widget(client_id, client_name, is_audio_on, is_video_on)
        self.chat_recipients.add(client_id, client_name)

    def create_video_grid(self):
        """ Creates the video grid. """
        self.ui.video_grid = VideoGrid(self.ui.video_grid_container)
        self.ui.video_grid_container_layout. \
            addWidget(self.ui.video_grid, 1, 1)  # 1, 1 because of the spacers

    def add_video_widget(self, client_id: bytes, client_name: str,
                         is_audio_on: bool, is_video_on: bool):
        """
        Creates a new ClientVideoWidget object and adds it to the video_grid.
        """
        video_widget = ClientVideoWidget(self.ui.video_grid,
                                         client_id, client_name,
                                         is_audio_on, is_video_on)
        done = self.ui.video_grid.add(video_widget)
        if done:
            self.video_widgets[client_id] = video_widget

    def remove_video_widget(self, client_id: bytes):
        """
        Removes the video widget of a client, given its id.
        """
        video_widget = self.video_widgets[client_id]
        self.ui.video_grid.remove(video_widget)
        del self.video_widgets[client_id]

    def show_video_frame(self, frame: np.ndarray, client_id: bytes):
        """
        Receives a frame and the id of the client who sent it,
        and displays the frame in the matching video widget.
        """
        # the frame might be received after the client left,
        # and then its video widget isn't in self.video_widgets
        if client_id in self.video_widgets:
            self.video_widgets[client_id].show_frame(frame)

    def init_chat(self):
        """ Initializes the chat. """
        self.ui.messages_layout.setAlignment(Qt.AlignTop)
        self.ui.chat_scroll_area.verticalScrollBar().rangeChanged.connect(
            self.scroll_chat_bar)
        self.chat_recipients = ChatRecipients(self.id)
        self.ui.recipient_combo_box.setModel(self.chat_recipients)

        # QLineEdit will emit the signal returnPressed()
        # whenever the user presses the enter key while in it
        self.ui.chat_input.returnPressed.connect(self.send_chat_msg)
        self.ui.chat_frame.hide()

    def scroll_chat_bar(self, start_range: int, end_range: int):
        """
        Scrolls the chat bar to the bottom.
        This method is called when the chat scroll bar
        range is changing (when the messages overflow it).
        """
        self.ui.chat_scroll_area.verticalScrollBar().setValue(end_range)

    def send_chat_msg(self):
        """
        Receives text from the user input
        and sends it as a chat message.
        """
        text = self.ui.chat_input.text()
        self.ui.chat_input.clear()
        if text == '':
            return

        # get the id of the selected recipient
        current_index = self.ui.recipient_combo_box.currentIndex()
        recipient_id = self.chat_recipients.item(current_index).data()

        msg = ChatMsg(self.id, recipient_id, text)
        msg.add_timestamp()  # TODO maybe do it on the server

        self.chat_client.send_msg(msg)
        self.show_chat_msg(msg)

    def show_chat_msg(self, msg: ChatMsg):
        """ Shows a given chat message. """
        sender_name = self.chat_recipients.get_name(msg.sender_id)
        recipient_name = self.chat_recipients.get_name(msg.recipient_id)

        msg_widget = MsgWidget(self.ui.messages_widget, msg, sender_name,
                               recipient_name)
        self.ui.messages_layout.addWidget(msg_widget)

    def create_shared_screen(self):
        """ Creates the shared screen. """
        self.ui.shared_screen = BasicVideoWidget(
            self.ui.main_vertical_splitter)
        self.ui.shared_screen.hide()

    def show_shared_screen(self, frame: np.ndarray, client_id: bytes):
        """ Shows a given frame in the shared screen. """
        # show the frame only if the shared screen is visible
        if self.ui.shared_screen.isVisible():
            self.ui.shared_screen.show_frame(frame)

    def create_smart_board(self):
        """ Creates the smart board. """
        self.ui.smart_board = SmartBoard(self.ui.main_vertical_splitter)
        self.ui.smart_board.new_painting.connect(
            self.info_client.send_painting_msg)
        self.ui.smart_board.hide()

    def init_remote_window(self):
        """ Initializes the remote window and creates its container. """
        # RemoteWindowContainer
        self.ui.remote_window_container = \
            RemoteWindowContainer(self.ui.main_vertical_splitter)
        self.ui.remote_window_container.remote_window.new_msg.connect(
            self.info_client.send_remote_window_msg)
        self.ui.remote_window_container.hide()

    def can_start_sharing(self) -> bool:
        """
        Checks if can start screen/smart_board/remote_window sharing -
        if none of the participants is already sharing.
        """
        # if one of these widgets is visible, someone is already sharing
        widgets = (self.ui.shared_screen, self.ui.smart_board,
                   self.ui.remote_window_container)
        for widget in widgets:
            if widget.isVisible():
                self.show_error_msg("Can't start sharing",
                                    "A participant is already sharing.")
                return False
        return True

    def can_toggle(self, widget: ToggleWidget) -> bool:
        """
        Returns True if the screen/smart_board/remote_window sharing widget
        can switch its state, False otherwise.
        """
        if widget.is_on:
            return True
        return self.can_start_sharing()

    def toggle_share_screen(self):
        """ Toggles the screen sharing. """
        toggled = self.toggle_sharing(self.ui.toggle_share_screen_widget,
                                      self.ui.shared_screen,
                                      Info.START_SCREEN_SHARING,
                                      Info.STOP_SCREEN_SHARING)
        if toggled:
            self.share_screen_client.toggle_is_sharing()

    def toggle_smart_board(self):
        """ Toggle the smart board sharing. """
        self.toggle_sharing(self.ui.toggle_smart_board_widget,
                            self.ui.smart_board,
                            Info.START_PAINTING, Info.STOP_PAINTING)

    def toggle_remote_window(self):
        """ Toggles the remote window. """
        self.toggle_sharing(self.ui.toggle_remote_window_widget,
                            self.ui.remote_window_container,
                            Info.START_REMOTE_WINDOW,
                            Info.STOP_REMOTE_WINDOW)

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
        if self.can_toggle(toggle_widget):
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
        self.ui.remote_window_container.set_main_window_pos(event.pos())

    def exit(self):
        """ Closes the clients and the gui. """
        print('active threads:', threading.active_count())
        for client in self.clients:
            client.close()
        self.close()  # close the gui

    @staticmethod
    def default_hspacer() -> QtWidgets.QSpacerItem:
        """ Returns a new horizontal spacer item with the default values. """
        return QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                     QtWidgets.QSizePolicy.Minimum)

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
