"""
    Hadar Shahar
    The info server code.
"""
import pickle
from typing import Callable
from network.tcp_network_utils import create_packet, send_packet, recv_packet
from network.custom_messages.general_info import Info
from server.broadcast_tcp_server import BroadcastTcpServer
from server.participant import Participant


class InfoServer(BroadcastTcpServer):
    """ Definition of the class InfoServer. """

    def __init__(self, ip: str, client_in_port: int, client_out_port: int,
                 client_disconnected_callback: Callable[[bytes], None],
                 client_id_validator: Callable[[bytes], bool]):
        """ Constructor. """
        super(InfoServer, self).__init__(ip, client_in_port, client_out_port,
                                         'info', client_id_validator)

        # this is a callback function in the main server
        self.client_disconnected_callback = client_disconnected_callback

        # these messages are related to the current sharing in every meeting
        # (screen sharing / smart board / remote window)
        # they will be sent to new client that connects to the meeting
        # { meeting_id: [status msg, ...] }
        self.last_status_msgs: [bytes, list] = {}

    def update_par_id(self, par: Participant) -> bool:
        """
        Validates the participant's id and if it's valid:
        updates the par object, receives the client info
        and calls the function sync_info.
        :returns: True if the client id is valid, False otherwise.
        """
        if not super(InfoServer, self).update_par_id(par):
            return False
        # TODO maybe get that from the auth server, but NOTE: here client_info.id also contains the meeting id
        par.client_info = pickle.loads(recv_packet(par.out_socket))
        self.sync_info(par)
        return True

    def sync_info(self, new_par: Participant):
        """
        Synchronizes the info between the new client
        and the other clients in the meeting.
        """
        with self.participants_lock:
            pars = self.participants[new_par.meeting_id]

            # send the other clients info to the new client
            msg = (Info.CLIENTS_INFO,
                   [par.client_info for client_id, par in pars.items()
                    if client_id != new_par.client_id])

        # send the last messages (related to sharing) to the new client
        for m in [msg] + self.last_status_msgs.get(new_par.meeting_id, []):
            send_packet(new_par.in_socket, pickle.dumps(m))

        # inform all the other clients that a new client has connected
        msg = (Info.NEW_CLIENT, new_par.client_info)
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
            par.client_info.is_audio_on = not par.client_info.is_audio_on
        elif msg_name == Info.TOGGLE_VIDEO:
            par.client_info.is_video_on = not par.client_info.is_video_on
        else:
            # if the message isn't an opposite message,
            # handle_opposite_msg won't do anything
            self.handle_opposite_msg(par, msg_name, msg_data)

        packet = create_packet(data)
        self.broadcast(par, packet)

    def handle_opposite_msg(self, sender_par: Participant, msg_name, msg_data):
        """
        Checks if a message received from sender_par is an opposite message
        (if it's in Info.OPPOSITE_MSGS).
        If it is, it handles the message, otherwise does nothing.
        """
        for start_msg, stop_msg in Info.OPPOSITE_MSGS.items():
            if msg_name == start_msg:
                if sender_par.meeting_id not in self.last_status_msgs:
                    self.last_status_msgs[sender_par.meeting_id] = []
                self.last_status_msgs[sender_par.meeting_id].append(
                    (msg_name, msg_data))

            elif msg_name == stop_msg:
                m = (start_msg, msg_data)
                self.last_status_msgs[sender_par.meeting_id].remove(m)

                # if there aren't any status messages, delete the empty list
                if not self.last_status_msgs[sender_par.meeting_id]:
                    del self.last_status_msgs[sender_par.meeting_id]

    def par_disconnected(self, par: Participant):
        """
        Receives a participant who has disconnected,
        and informs all the other participants.
        """
        super(InfoServer, self).par_disconnected(par)
        full_par_id = par.meeting_id + par.client_id

        msgs_to_remove = []
        for msg in self.last_status_msgs.get(par.meeting_id, []):
            msg_name, msg_data = msg
            # if the client who left was in the middle of a sharing
            # inform all the participants that he has stopped sharing
            if full_par_id == msg_data:
                msgs_to_remove.append(msg)
                if msg_name in Info.OPPOSITE_MSGS:
                    broadcast_msg = (Info.OPPOSITE_MSGS[msg_name], full_par_id)
                    self.broadcast_info_msg(par, broadcast_msg)

        if msgs_to_remove:
            for msg in msgs_to_remove:
                self.last_status_msgs[par.meeting_id].remove(msg)

            # if there aren't any status messages,
            # delete the empty list in the dict
            if not self.last_status_msgs[par.meeting_id]:
                del self.last_status_msgs[par.meeting_id]

        # inform all the others participants that he left
        msg = (Info.CLIENT_LEFT, full_par_id)
        self.broadcast_info_msg(par, msg)

        # inform the main server that that client has disconnected
        self.client_disconnected_callback(full_par_id)
