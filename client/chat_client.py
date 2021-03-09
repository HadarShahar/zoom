"""
    Hadar Shahar
    The chat client code.
"""
import pickle
from PyQt5.QtCore import pyqtSignal
from network.tcp_network_utils import recv_packet
from network.custom_messages.chat_msg import ChatMsg
from client.network_constants import Constants
from client.basic_tcp_client import BasicTcpClient


class ChatClient(BasicTcpClient):
    """ Definition of the class ChatClient. """

    # this signal is emitted when a new chat message is received
    new_msg = pyqtSignal(ChatMsg)

    def __init__(self, client_id: bytes):
        """ Constructor. """
        super(ChatClient, self).__init__(
            Constants.SERVER_IP, Constants.CLIENT_IN_CHAT_PORT,
            Constants.CLIENT_OUT_CHAT_PORT, client_id)

    def send_data_loop(self):
        """
        Just overrides the abstract method in the base class.
        """
        pass

    def receive_data_loop(self):
        """
        Receives chat messages from the server
        and forwards them to the main window using the new_msg signal.
        """
        while self.running:
            msg = pickle.loads(recv_packet(self.in_socket))
            self.new_msg.emit(msg)

    def send_msg(self, msg: ChatMsg):
        """
        Receives a message, converts it to bytes
        and sends it to the server.
        """
        self.send_packet(pickle.dumps(msg))
