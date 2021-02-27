"""
    Hadar Shahar
    The info client code.
"""
from typing import Union
import pickle
from PyQt5.QtCore import pyqtSignal
from tcp_network_protocol import recv_packet
from constants import Info
from client.network_constants import Constants
from client.basic_tcp_client import BasicTcpClient
from custom_messages.painting import Painting
from custom_messages.client_info import ClientInfo
from custom_messages.remote_window_msg import RemoteWindowMsg


class InfoClient(BasicTcpClient):
    """ Definition of the class InfoClient. """

    new_info = pyqtSignal(tuple)

    def __init__(self, client_info: ClientInfo):
        """ Constructor. """
        super(InfoClient, self).__init__(
            Constants.SERVER_IP, Constants.CLIENT_IN_INFO_PORT,
            Constants.CLIENT_OUT_INFO_PORT, client_info.id)

        # send all the client info to the server
        self.send_info_msg(client_info)

    def send_data_loop(self):
        """
        Just overrides the function in BasicClient.
        """
        pass

    def receive_data_loop(self):
        """
        Receives messages from the InfoServer
        and forwards them to the main window using the new_msg signal.
        """
        while self.running:
            # tuple of the msg name and the msg data
            full_msg = pickle.loads(recv_packet(self.in_socket))

            # emit a signal indicating that new info was received
            self.new_info.emit(full_msg)

    def send_toggle_msg(self, toggle_type: int):
        """ Sends a toggle message of a given type. """
        self.send_info_msg((toggle_type, self.id))

    def send_painting_msg(self, painting: Painting):
        """ Sends a given painting message. """
        self.send_info_msg((Info.NEW_PAINTING, painting))

    def send_remote_window_msg(self, msg: RemoteWindowMsg):
        """ Sends a given remote window message. """
        self.send_info_msg((Info.REMOTE_WINDOW_MSG, msg))

    def send_info_msg(self, msg: Union[tuple, ClientInfo]):
        """ Sends a given info message. """
        self.send_packet(pickle.dumps(msg))
