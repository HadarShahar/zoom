"""
    Hadar Shahar
    The chat client code.
"""
from PyQt5.QtCore import pyqtSignal
from network_protocol import send_packet, recv_packet
from chat_msg import ChatMsg
from client.basic_client import BasicClient
import pickle


class ChatClient(BasicClient):
    """ definition of the class ChatClient """

    new_msg = pyqtSignal(ChatMsg)

    def __init__(self, ip: str, in_socket_port: int,
                 out_socket_port: int, client_id: bytes):
        """ constructor """
        super(ChatClient, self).__init__(ip, in_socket_port,
                                         out_socket_port, client_id)

    def send_data_loop(self):
        """
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
        send_packet(self.out_socket, pickle.dumps(msg))
