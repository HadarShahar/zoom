"""
    Hadar Shahar
    BasicTcpClient.
"""
import socket
import sys
from abc import ABC
from client.basic_client import BasicClient
from constants import EXIT_SIGN
from tcp_network_protocol import create_packet


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

        except socket.error as msg:  # TODO nice exit
            print('Connection failure: %s\n terminating program' % msg)
            sys.exit(1)

    def send_packet(self, data: bytes):
        """ Creates a packet of data and sends it.  """
        self.out_socket.send(create_packet(data))
        # TODO: maybe use sendall
        # if len(data) != sent:
        #     print(len(data), sent)

    def close(self):
        """
        Sends the server EXIT_SIGN (if the output socket is open)
        and closes the sockets.
        """
        super(BasicTcpClient, self).close()
        # if self.out_socket.fileno() != -1:
        # fileno() will return -1 for closed sockets.
        if not self.out_socket._closed:
            self.send_packet(EXIT_SIGN)
        self.in_socket.close()
        self.out_socket.close()
