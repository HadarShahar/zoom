"""
    Hadar Shahar
    BasicUdpClient.
"""
import socket
import struct
from abc import ABC
from typing import Union, Tuple
from client.basic_client import BasicClient
from network.constants import NETWORK_BYTES_FORMAT, NETWORK_BYTES_PER_NUM, \
    UDP_SOCKET_BUFFER_SIZE, UDP_NEW_CLIENT_MSG


class BasicUdpClient(BasicClient, ABC):
    """ Definition of the abstract class BasicUdpClient. """

    def __init__(self, ip: str, in_socket_port: int, out_socket_port: int,
                 client_id: bytes, is_sharing=True):
        """ Initializes input and output sockets. """
        super(BasicUdpClient, self).__init__(client_id, is_sharing)

        self.in_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_out_address = (ip, in_socket_port)
        self.out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_in_address = (ip, out_socket_port)

        # inform the server that a new client has connected
        # NOTE: this message must be sent from the input socket,
        #       so the server will know where to send the data to.
        self.in_socket.sendto(self.pack_data(UDP_NEW_CLIENT_MSG),
                              self.server_in_address)

    def pack_data(self, data: bytes) -> bytes:
        """
        Packs the data prefixed with the client id's length
        and the client id, so it's ready to be sent to the server.
        <padded_id_len><id><data>
       """
        padded_id_len = struct.pack(NETWORK_BYTES_FORMAT, len(self.id))
        return padded_id_len + self.id + data

    def send_data(self, data: bytes):
        """ Packs and sends data to the server. """
        self.out_socket.sendto(self.pack_data(data), self.server_in_address)

    def receive_data(self) -> Union[Tuple[bytes, bytes], Tuple[None, None]]:
        """
        Receives data from the server.
        Returns the sender client id and the data that was received
        if it was received from the right server.
        Otherwise returns (None, None).
        """
        data, address = self.in_socket.recvfrom(UDP_SOCKET_BUFFER_SIZE)
        if address != self.server_out_address:
            print(f"The data received from {address}, but the server address "
                  f"is {self.server_out_address}. Ignoring the data.")
            print(self.server_in_address)
            return None, None

        n = NETWORK_BYTES_PER_NUM
        # struct.unpack always returns a tuple
        id_len = struct.unpack(NETWORK_BYTES_FORMAT, data[:n])[0]
        sender_id = data[n: n + id_len]
        content = data[n + id_len:]
        return sender_id, content

    def close(self):
        """
        Closes the sockets.
        """
        super(BasicUdpClient, self).close()
        self.in_socket.close()
        self.out_socket.close()
