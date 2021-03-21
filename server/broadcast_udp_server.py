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

    def __init__(self, ip: str, client_in_port: int, client_out_port: int,
                 server_name: str, client_id_validator):
        """ Initializes input and output sockets. """
        super(BroadcastUdpServer, self).__init__()
        self.server_name = server_name
        self.client_id_validator = client_id_validator
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

    def check_client_id(self, client_id: bytes) -> bool:
        """
        Checks the client id.
        :param client_id: the client id to be checked.
        :returns: True if it's valid, False otherwise.
        """
        # here self.clients_addresses_lock is already acquired
        # there must not be a participant with the same id!
        if client_id in [client_id in self.clients_addresses.keys()] or \
                (not self.client_id_validator(client_id)):
            print(f'Invalid id: {client_id}, ignoring the participant.')
            return False
        return True

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
                        # if it's a new client, check its id
                        if not self.check_client_id(client_id):
                            return
                        self.clients_addresses[client_id] = client_address
                        print(f'{self.server_name} participants:',
                              list(self.clients_addresses.values()))
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
            print(f'{self.server_name} participants:',
                  list(self.clients_addresses.values()))
