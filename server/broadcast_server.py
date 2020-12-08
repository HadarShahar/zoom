"""
    Hadar Shahar
    The broadcast server code.
"""
import socket
import sys
import threading
from constants import NUMBER_OF_WAITING_CONNECTIONS, EXIT_SIGN
from server.participant import Participant
from network_protocol import create_packet, send_packet, recv_packet


class BroadcastServer(threading.Thread):
    """ Definition of the class BroadcastServer. """

    def __init__(self, ip: str, client_in_port: int,
                 client_out_port: int, server_name: str):
        """
        Initializes input and output sockets for the BroadcastServer.
        """
        super(BroadcastServer, self).__init__()
        self.server_name = server_name
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

            # TODO: maybe add a lock
            # participants that are connecting to the meeting
            # {hostaddr: Participant(...)}
            self.connecting_pars: [str, Participant] = {}

            # connected participants in the meeting
            # {par_id: Participant(...)}
            self.participants: [bytes, Participant] = {}

        except socket.error as msg:
            print(f'{self.server_name} connection failure: {msg}')
            sys.exit(1)

    # def run(self):
    #     """
    #     """
    #     threading.Thread(target=self.accept_out_socket).start()
    #     threading.Thread(target=self.accept_in_socket).start()
    #
    # def accept_out_socket(self):
    #     """
    #     accept clients that connect to the out_socket
    #     """
    #     while True:
    #         client_in_socket, address = self.accept_clients_in.accept()
    #         hostaddr, port = address
    #         if hostaddr in self.connecting_pars:
    #             par = self.connecting_pars[hostaddr]
    #             par.in_socket = client_in_socket
    #             self.add_participant(par)
    #         else:
    #             self.connecting_pars[hostaddr] = \
    #                 Participant(address, in_socket=client_in_socket)
    #
    # def accept_in_socket(self):
    #     """
    #     accept clients that connect to the in_socket
    #     """
    #     while True:
    #         client_out_socket, address = self.accept_clients_out.accept()
    #         hostaddr, port = address
    #         if hostaddr in self.connecting_pars:
    #             par = self.connecting_pars[hostaddr]
    #             par.out_socket = client_out_socket
    #             self.add_participant(par)
    #         else:
    #             self.connecting_pars[hostaddr] = \
    #                 Participant(address, out_socket=client_out_socket)

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

    def update_par_id(self, par: Participant):
        """
        Updates the participant id.
        This method receives the id from the client,
        but the InfoServer overrides this method and
        assigns an id to the client.
        """
        par.id = bytes(recv_packet(par.out_socket))

    def handle_participant(self, par: Participant):
        """
        Handles a given participant.
        """
        try:
            self.update_par_id(par)
            self.participants[par.id] = par
            # print(f'New participant: {par}')
            print(f'{self.server_name} participants:',
                  self.participants.values())

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
        id_packet = create_packet(par.id)
        data_packet = create_packet(data)
        self.broadcast(par, (id_packet + data_packet))

    def par_disconnected(self, par: Participant):
        """
        Receives a participant who has disconnected,
        closes its sockets and removes it from the participants list.
        """
        # print(f'{par} has disconnected')
        par.close_sockets()
        if par.id in self.participants:
            del self.participants[par.id]
        print(f'{self.server_name} participants:', self.participants.values())

    def broadcast(self, sender_par: Participant, packet: bytes):
        """
        Broadcasts a given packet (or chained packets) of data
        to all the participants, except the one who sends the data.
        """
        for par_id, par in self.participants.items():
            if par != sender_par:
                # if True:  # TODO delete it (just for debugging)!
                with par.lock:
                    par.in_socket.send(packet)  # TODO maybe use sendall
                    # send_packet(par.in_socket, sender_par.id)
                    # send_packet(par.in_socket, data)
