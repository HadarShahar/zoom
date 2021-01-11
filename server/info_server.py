"""
    Hadar Shahar
    The info server code.
"""
import pickle
from tcp_network_protocol import create_packet, send_packet, recv_packet
from constants import Info
from server.broadcast_tcp_server import BroadcastTcpServer
from server.participant import Participant


class InfoServer(BroadcastTcpServer):
    """ Definition of the class InfoServer. """

    next_client_id = 0

    def __init__(self, ip: str, client_in_port: int, client_out_port: int):
        """ Constructor. """
        super(InfoServer, self).__init__(ip, client_in_port,
                                         client_out_port, 'info')

        # these messages are related to the current sharing
        # (screen sharing / smart board / remote window)
        # they will be sent to new client that connect to the meeting
        self.last_status_msgs = []

    def update_par_id(self, par: Participant):
        """
        Receives the client name, and send the client its id.
        Then updates the info between all the clients.
        """
        par.name = recv_packet(par.out_socket).decode()

        InfoServer.next_client_id += 1
        par.id = str(InfoServer.next_client_id).encode()
        send_packet(par.in_socket, par.id)

        self.update_info(par)

    def update_info(self, new_par: Participant):
        """
        Updates the info between the new client
        and the other clients in the meeting.
        """
        # send the other clients info to the new client
        msg = (Info.CLIENTS_INFO,
               [p.get_info() for p in self.participants.values()])
        # send the last messages (related to sharing) to the new client
        for m in [msg] + self.last_status_msgs:
            send_packet(new_par.in_socket, pickle.dumps(m))

        # inform all the other clients that a new client has connected
        msg = (Info.NEW_CLIENT, new_par.get_info())
        self.broadcast_info_msg(new_par, msg)

    def broadcast_info_msg(self, sender_par: Participant, msg: tuple):
        """
        Broadcasts a given info msg to all the participants,
        except the one who sends it.
        """
        packet = create_packet(pickle.dumps(msg))
        self.broadcast(sender_par, packet)

    def handle_new_data(self, par: Participant, data: bytes):
        """
        Handles new data received from a given participant.
        """
        msg_name, msg_data = pickle.loads(data)
        if msg_name == Info.TOGGLE_AUDIO:
            par.is_audio_on = not par.is_audio_on
        elif msg_name == Info.TOGGLE_VIDEO:
            par.is_video_on = not par.is_video_on

        elif msg_name in Info.OPPOSITE_MSGS:
            self.last_status_msgs.append((msg_name, msg_data))
        else:

            for start_msg, stop_msg in Info.OPPOSITE_MSGS.items():
                if msg_name == stop_msg:
                    self.last_status_msgs.remove((start_msg, msg_data))

        packet = create_packet(data)
        self.broadcast(par, packet)

    def par_disconnected(self, par: Participant):
        """
        Receives a participant who has disconnected,
        and informs all the other participants.
        """
        super(InfoServer, self).par_disconnected(par)

        # if the participant didn't have an id before he left
        if par.id == b'':
            return

        msgs_to_remove = []
        for msg in self.last_status_msgs:
            msg_name, msg_data = msg
            # if the client who left was sharing screen / painting
            # inform all the  participants that he has stopped sharing
            if par.id == msg_data:
                msgs_to_remove.append(msg)
                if msg_name in Info.OPPOSITE_MSGS:
                    broadcast_msg = (Info.OPPOSITE_MSGS[msg_name], par.id)
                    self.broadcast_info_msg(par, broadcast_msg)

        for msg in msgs_to_remove:
            self.last_status_msgs.remove(msg)

        # inform all the others participants that he left
        msg = (Info.CLIENT_LEFT, par.id)
        self.broadcast_info_msg(par, msg)
