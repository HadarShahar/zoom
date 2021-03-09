"""
    Hadar Shahar
    BroadcastUdpServer.
"""
import socket
import sys
import threading
import struct
from network.constants import NETWORK_BYTES_FORMAT, NETWORK_BYTES_PER_NUM, \
    UDP_SOCKET_BUFFER_SIZE, UDP_NEW_CLIENT_MSG


class BroadcastUdpServer(threading.Thread):
    """ Definition of the class BroadcastUdpServer. """

    def __init__(self, ip: str, client_in_port: int,
                 client_out_port: int, server_name: str):
        """ Initializes input and output sockets. """
        super(BroadcastUdpServer, self).__init__()
        self.server_name = server_name
        try:
            self.out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.out_socket.bind((ip, client_in_port))

            self.in_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.in_socket.bind((ip, client_out_port))

            print(f'{self.server_name} server listening on ports '
                  f'{client_in_port}, {client_out_port}')

            # {client_id: client_in_address}
            self.clients_addresses: [bytes, (str, int)] = {}
            self.clients_addresses_lock = threading.Lock()

        except socket.error as msg:
            print(f'{self.server_name} connection failure: {msg}')
            sys.exit(1)

    def run(self):
        """ Starts a thread that receives and broadcasts data. """
        threading.Thread(target=self.receive_and_broadcast).start()

    def receive_and_broadcast(self):
        """
        Receives data and broadcasts it to all the other clients,
        if it was sent from a known client.
        If it was sent from a new client and the client wants to connect
        (if it sends a UDP_NEW_CLIENT_MSG) add the client.
        """
        try:
            while True:
                data, client_address = self.in_socket.recvfrom(
                    UDP_SOCKET_BUFFER_SIZE)

                n = NETWORK_BYTES_PER_NUM
                # struct.unpack always returns a tuple
                id_len = struct.unpack(NETWORK_BYTES_FORMAT, data[:n])[0]
                client_id = data[n: n + id_len]
                content = data[n + id_len:]

                with self.clients_addresses_lock:
                    if client_id in self.clients_addresses:
                        # if it's a known client
                        self.broadcast(client_id, data)
                    elif content.startswith(UDP_NEW_CLIENT_MSG):
                        # if it's a new client
                        self.clients_addresses[client_id] = client_address
                        print(f'{self.server_name} participants: '
                              f'{self.clients_addresses.keys()}')
                    else:
                        print('malformed packet.')

        except socket.error as e:
            print(f'{self.server_name} receive_and_broadcast: {e}')

    def broadcast(self, sender_id: bytes, packet: bytes):
        """
        Broadcasts a given packet (or chained packets) of data
        to all the participants, except the one who sends the data.
        """
        for client_id, client_in_address in self.clients_addresses.items():
            if client_id != sender_id:
                self.out_socket.sendto(packet, client_in_address)

    def client_disconnected(self, client_id: bytes):
        """
        The main server calls this function when a client disconnects.
        It removes it from clients_addresses.
        """
        with self.clients_addresses_lock:
            if client_id in self.clients_addresses:
                del self.clients_addresses[client_id]
            print(f'{self.server_name} participants: '
                  f'{self.clients_addresses.keys()}')
