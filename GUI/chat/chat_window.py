"""
    Hadar Shahar
    The chat window.
"""
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt

from GUI.chat.msg_widget import MsgWidget
from GUI.chat.chat_recipients import ChatRecipients
from client.chat_client import ChatClient
from custom_messages.chat_msg import ChatMsg
from GUI.gui_constants import CHAT_WINDOW_UI_FILEPATH


class ChatWindow(QtWidgets.QWidget):
    """ Definition of the class ChatWindow. """

    def __init__(self, client_id: bytes, parent: QtWidgets.QWidget):
        """ Constructor. """
        super(ChatWindow, self).__init__(parent)
        uic.loadUi(CHAT_WINDOW_UI_FILEPATH, self)
        self.client_id = client_id

        self.client = ChatClient(self.client_id)
        self.client.new_msg.connect(self.show_chat_msg)
        self.client.start()

        self.messages_layout.setAlignment(Qt.AlignTop)
        self.chat_scroll_area.verticalScrollBar().rangeChanged.connect(
            self.scroll_chat_bar)
        self.recipients = ChatRecipients(self.client_id)
        self.recipient_combo_box.setModel(self.recipients)

        # QLineEdit will emit the signal returnPressed()
        # whenever the user presses the enter key while in it
        self.chat_input.returnPressed.connect(self.send_chat_msg)
        self.hide()

    def scroll_chat_bar(self, start_range: int, end_range: int):
        """
        Scrolls the chat bar to the bottom.
        This method is called when the chat scroll bar
        range is changing (when the messages overflow it).
        """
        self.chat_scroll_area.verticalScrollBar().setValue(end_range)

    def send_chat_msg(self):
        """
        Receives text from the user input
        and sends it as a chat message.
        """
        text = self.chat_input.text()
        self.chat_input.clear()
        if text == '':
            return

        # get the id of the selected recipient
        current_index = self.recipient_combo_box.currentIndex()
        recipient_id = self.recipients.item(current_index).data()

        msg = ChatMsg(self.client_id, recipient_id, text)
        msg.add_timestamp()

        self.client.send_msg(msg)
        self.show_chat_msg(msg)

    def show_chat_msg(self, msg: ChatMsg):
        """ Shows a given chat message. """
        sender_name = self.recipients.get_name(msg.sender_id)
        recipient_name = self.recipients.get_name(msg.recipient_id)

        msg_widget = MsgWidget(self.messages_widget, msg, sender_name,
                               recipient_name)
        self.messages_layout.addWidget(msg_widget)

    def add_client(self, client_id: bytes, client_name: str):
        """ Adds a client to the chat recipients. """
        self.recipients.add(client_id, client_name)

    def remove_client(self, client_id: bytes):
        """ Removes a client from the chat recipients. """
        self.recipients.remove(client_id)
