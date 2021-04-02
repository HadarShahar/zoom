"""
    Hadar Shahar
    BroadcastUdpServer.
"""
import socket
import sys
import threading
import struct
from typing import Dict
from network.constants import NETWORK_BYTES_FORMAT, NETWORK_BYTES_PER_NUM, \
    UDP_SOCKET_BUFFER_SIZE, UDP_NEW_CLIENT_MSG
from server.ids_config import MEETING_ID_LEN, CLIENT_ID_LEN


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

            # { meeting_id: {client_id: client_in_address} }
            self.clients_addresses: Dict[bytes, Dict[bytes, (str, int)]] = {}
            self.clients_addresses_lock = threading.Lock()

        except socket.error as msg:
            print(f'{self.server_name} connection failure: {msg}')
            sys.exit(1)

    def run(self):
        """ Runs in a separate thread, receives and broadcasts data. """
        self.receive_and_broadcast()

    def add_new_client(self, meeting_id: bytes, client_id: bytes,
                       client_address: (str, int)):
        """
        Tries to add a new client to the meeting with the id meeting_id.
        """
        success = self.client_id_validator(meeting_id + client_id)

        if success:
            with self.clients_addresses_lock:
                if meeting_id in self.clients_addresses:
                    # there must not be a participant with the same id!
                    if client_id in self.clients_addresses[meeting_id]:
                        success = False
                    else:
                        self.clients_addresses[meeting_id][client_id] = \
                            client_address
                else:
                    self.clients_addresses[meeting_id] = \
                        {client_id: client_address}

        if success:
            self.print_clients()
        else:
            print(f'Invalid id: {client_id}, ignoring the participant')

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
                received_id = data[n: n + id_len]

                if len(received_id) != MEETING_ID_LEN + CLIENT_ID_LEN:
                    print(f'Invalid id (len={len(received_id)}).')
                    continue
                meeting_id = received_id[:MEETING_ID_LEN]
                client_id = received_id[MEETING_ID_LEN:]
                content = data[n + id_len:]

                with self.clients_addresses_lock:
                    is_known_client = \
                        meeting_id in self.clients_addresses and \
                        client_id in self.clients_addresses[meeting_id]

                if is_known_client:
                    self.broadcast(meeting_id, client_id, data)
                elif content.startswith(UDP_NEW_CLIENT_MSG):
                    # if it's a new client
                    self.add_new_client(meeting_id, client_id,
                                        client_address)
                else:
                    print('malformed packet.')

        except socket.error as e:
            print(f'{self.server_name} receive_and_broadcast: {e}')

    def broadcast(self, meeting_id: bytes, sender_client_id: bytes,
                  packet: bytes):
        """
        Broadcasts a given packet (or chained packets) of data
        to all the participants in the meeting,
        except the one who sends the data.
        """
        with self.clients_addresses_lock:
            addresses = self.clients_addresses[meeting_id]
            for client_id, client_in_address in addresses.items():
                if client_id != sender_client_id:
                    self.out_socket.sendto(packet, client_in_address)

    def client_disconnected(self, full_client_id: bytes):
        """
        The main server calls this function when a client disconnects.
        It removes it from clients_addresses.
        """
        meeting_id = full_client_id[:MEETING_ID_LEN]
        client_id = full_client_id[MEETING_ID_LEN:]
        with self.clients_addresses_lock:
            clients_in_meeting = self.clients_addresses.get(meeting_id)
            if clients_in_meeting and client_id in clients_in_meeting:
                del clients_in_meeting[client_id]

                # if the meeting is now empty, delete the meeting id
                if not self.clients_addresses[meeting_id]:
                    del self.clients_addresses[meeting_id]

            self.print_clients()

    def print_clients(self):
        """ Prints the server clients. """
        print(f'{self.server_name} clients:',
              {meeting_id.hex(): list(addresses.values())
               for meeting_id, addresses in self.clients_addresses.items()})
