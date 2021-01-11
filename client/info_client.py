"""
    Hadar Shahar
    The info client code.
"""
import pickle
from PyQt5.QtCore import pyqtSignal
from tcp_network_protocol import send_packet, recv_packet
from constants import Info
from client.basic_tcp_client import BasicTcpClient
from custom_messages.painting import Painting
from custom_messages.remote_window_msg import RemoteWindowMsg


class InfoClient(BasicTcpClient):
    """ Definition of the class InfoClient. """

    new_info = pyqtSignal(tuple)

    def __init__(self, ip: str, in_socket_port: int, out_socket_port: int):
        """ Constructor. """
        # this id is just for the BasicClient constructor,
        # it will change when the overridden method update_id() will be called.
        temporary_id = b''
        super(InfoClient, self).__init__(ip, in_socket_port,
                                         out_socket_port, temporary_id)

        self.clients_info = {}  # {client_id: client_name}

    def update_id(self):
        """
        Sends the client name to the server,
        and receives the client id from the server.
        """
        self.name = ''
        while self.name == '':
            self.name = input('Enter your name: ')
        send_packet(self.out_socket, self.name.encode())

        self.id = bytes(recv_packet(self.in_socket))
        print('my id:', self.id)

    def send_data_loop(self):
        """
        Just overrides the function in BasicClient.
        """
        pass

    def receive_data_loop(self):
        """
        Receives messages from the InfoServer
        and updates the clients_info accordingly.
        """
        while self.running:
            # tuple of the msg name and the msg data
            full_msg = pickle.loads(recv_packet(self.in_socket))

            # emit a signal indicating that new info was received
            self.new_info.emit(full_msg)

            msg_name, msg_data = full_msg
            if msg_name == Info.NEW_CLIENT:
                client_id, client_name, _, _ = msg_data
                self.clients_info[client_id] = client_name
            elif msg_name == Info.CLIENTS_INFO:
                # in this case msg_data is a list ot tuples
                for client_id, client_name, _, _ in msg_data:
                    self.clients_info[client_id] = client_name
            elif msg_name == Info.CLIENT_LEFT:
                # in this case msg_data = client_id
                del self.clients_info[msg_data]
            else:
                continue

            print('clients_info:', self.clients_info)

    def send_toggle_msg(self, toggle_type: int):
        """ Sends a toggle message of a given type. """
        self.send_info_msg((toggle_type, self.id))

    def send_painting_msg(self, painting: Painting):
        """ Sends a given painting message. """
        self.send_info_msg((Info.NEW_PAINTING, painting))

    def send_remote_window_msg(self, msg: RemoteWindowMsg):
        """ Sends a given remote window message. """
        self.send_info_msg((Info.REMOTE_WINDOW_MSG, msg))

    def send_info_msg(self, msg: tuple):
        """ Sends a given info message. """
        send_packet(self.out_socket, pickle.dumps(msg))


