"""
    Hadar Shahar
    BasicTcpClient.
"""
import socket
from abc import ABC
from client.basic_client import BasicClient
from network.constants import EXIT_SIGN
from network.tcp_network_utils import create_packet


class BasicTcpClient(BasicClient, ABC):
    """ Definition of the abstract class BasicTCPClient. """

    def __init__(self, ip: str, in_socket_port: int, out_socket_port: int,
                 client_id: bytes, is_sharing=True):
        """ Initializes input and output sockets. """
        super(BasicTcpClient, self).__init__(client_id, is_sharing)
        try:
            self.in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.in_socket.connect((ip, in_socket_port))

            self.out_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.out_socket.connect((ip, out_socket_port))

            # send the client id to the server
            self.send_packet(self.id)

        except socket.error as e:
            # prints the full class name and the exception
            print(type(self), e)
            raise e  # will be handled in the main window

    def send_packet(self, data: bytes):
        """ Creates a packet of data and sends it.  """
        try:
            self.out_socket.sendall(create_packet(data))
        except socket.error as e:
            if self.running:
                # prints the full class name and the exception
                print(type(self), e)
                self.network_error.emit(str(e))

    def close(self):
        """
        Sends the server EXIT_SIGN (if the output socket is open)
        and closes the sockets.
        """
        super(BasicTcpClient, self).close()
        # if self.out_socket.fileno() != -1:
        # fileno() will return -1 for closed sockets.
        # if not self.out_socket._closed:
        self.send_packet(EXIT_SIGN)
        self.in_socket.close()
        self.out_socket.close()
