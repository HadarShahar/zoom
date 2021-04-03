"""
    Hadar Shahar
    BroadcastTcpServer.
"""
import socket
import sys
import threading
from typing import Dict
from network.constants import NUMBER_OF_WAITING_CONNECTIONS, EXIT_SIGN
from server.participant import Participant
from network.tcp_network_utils import create_packet, recv_packet
from server.ids_config import MEETING_ID_LEN


class BroadcastTcpServer(threading.Thread):
    """ Definition of the class BroadcastTcpServer. """

    def __init__(self, ip: str, client_in_port: int, client_out_port: int,
                 server_name: str, client_id_validator):
        """
        Initializes input and output sockets for the BroadcastServer.
        """
        super(BroadcastTcpServer, self).__init__()
        self.server_name = server_name
        self.client_id_validator = client_id_validator
        try:
            # socket that accepts each client input socket
            self.accept_clients_in = socket.socket(socket.AF_INET,
                                                   socket.SOCK_STREAM)
            self.accept_clients_in.bind((ip, client_in_port))
            self.accept_clients_in.listen(NUMBER_OF_WAITING_CONNECTIONS)

            # socket that accepts each client output socket
            self.accept_clients_out = socket.socket(socket.AF_INET,
                                                    socket.SOCK_STREAM)
            self.accept_clients_out.bind((ip, client_out_port))
            self.accept_clients_out.listen(NUMBER_OF_WAITING_CONNECTIONS)

            print(f'{self.server_name} server listening on ports '
                  f'{client_in_port}, {client_out_port}')

            # participants that are connecting to the meeting
            # {hostaddr: Participant(...)}
            self.connecting_pars: [str, Participant] = {}
            self.connecting_pars_lock = threading.Lock()

            # connected participants in the meetings
            # { meeting_id: {client_id: Participant(...), ...} }
            self.participants: Dict[bytes, Dict[bytes, Participant]] = {}
            self.participants_lock = threading.Lock()

        except socket.error as msg:
            print(f'{self.server_name} connection failure: {msg}')
            sys.exit(1)

    def run(self):
        """
        Starts 2 threads,
        one the accepts the clients' input socket
        and another one the accepts the clients' output socket.
        """
        threading.Thread(target=self.accept_clients_sockets,
                         args=(self.accept_clients_in, 'in_socket')).start()
        threading.Thread(target=self.accept_clients_sockets,
                         args=(self.accept_clients_out, 'out_socket')).start()

    def accept_clients_sockets(self, sock: socket.socket,
                               client_sock_name: str):
        """
        Accepts clients that connect to a given socket,
        and creates a Participant object for each client.
        When a participant has done connecting,
        it calls the add_participant method.

        :param sock: accept clients that connect to this socket
        :param client_sock_name: 'in_socket' / 'out_socket'
        """
        while True:
            client_socket, address = sock.accept()
            hostaddr, port = address
            with self.connecting_pars_lock:
                if hostaddr in self.connecting_pars:
                    par = self.connecting_pars[hostaddr]
                    setattr(par, client_sock_name, client_socket)
                    self.add_participant(par)
                else:
                    par = Participant(address)
                    setattr(par, client_sock_name, client_socket)
                    self.connecting_pars[hostaddr] = par

    def add_participant(self, par: Participant):
        """
        Adds a given participant to the meeting,
        and opens a new thread for handling it.
        """
        # if the participant has connected to the server
        # via input and output sockets
        if par.done_connecting():
            # remove the participant from the connecting_pars dictionary
            hostaddr, port = par.address
            del self.connecting_pars[hostaddr]

            # handle the participant in a separate thread
            threading.Thread(target=self.handle_participant,
                             args=(par,)).start()

    def update_par_id(self, par: Participant) -> bool:
        """
        This method receives the id from the client, validates it
        and updates the par object if it's valid.
        :returns: True if the client id is valid, False otherwise.
        """
        received_id = bytes(recv_packet(par.out_socket))

        success = self.client_id_validator(received_id)
        if success:
            par.meeting_id = received_id[:MEETING_ID_LEN]
            par.client_id = received_id[MEETING_ID_LEN:]

            # "with" block always executes, even after return!
            with self.participants_lock:
                if par.meeting_id in self.participants:
                    # there must not be a participant with the same id!
                    if par.client_id in self.participants[par.meeting_id]:
                        success = False
                    else:
                        self.participants[par.meeting_id][par.client_id] = par
                else:
                    self.participants[par.meeting_id] = {par.client_id: par}

        if success:
            self.print_participants()
        else:
            print(f'Invalid id: {received_id}, ignoring the participant.')
        return success

    def handle_participant(self, par: Participant):
        """
        Handles a given participant.
        """
        try:
            if not self.update_par_id(par):
                return

            while True:
                data = recv_packet(par.out_socket)
                # if the client wants to disconnect, it sends an EXIT_SIGN
                if data == EXIT_SIGN:
                    break
                else:
                    self.handle_new_data(par, data)
        except socket.error as e:
            print(f'{self.server_name} handle_participant {par}: {e}')
        finally:
            self.par_disconnected(par)

    def handle_new_data(self, par: Participant, data: bytes):
        """
        Handles new data that was received from a given participant.
        """
        id_packet = create_packet(par.meeting_id + par.client_id)
        data_packet = create_packet(data)
        self.broadcast(par, (id_packet + data_packet))

    def par_disconnected(self, par: Participant):
        """
        Receives a participant who has disconnected,
        closes its sockets and removes it from the participants in the meeting.
        """
        # print(f'{par} has disconnected')
        par.close_sockets()
        with self.participants_lock:
            pars_in_meeting = self.participants[par.meeting_id]
            if pars_in_meeting and par.client_id in pars_in_meeting:
                del pars_in_meeting[par.client_id]

                # if the meeting is now empty, delete the meeting id
                if not self.participants[par.meeting_id]:
                    del self.participants[par.meeting_id]

            self.print_participants()

    def broadcast(self, sender_par: Participant, packet: bytes):
        """
        Broadcasts a given packet (or chained packets) of data
        to all the participants in the meeting of the sending participant,
        except the one who sends the data.
        """
        with self.participants_lock:
            pars = self.participants.get(sender_par.meeting_id, {})
            for par_id, par in pars.items():
                if par_id != sender_par.client_id:
                    with par.lock:
                        par.in_socket.sendall(packet)

    def print_participants(self):
        """ Prints the server participants. """
        print(f'{self.server_name} participants:',
              {meeting_id.hex(): list(pars.values())
               for meeting_id, pars in self.participants.items()})
