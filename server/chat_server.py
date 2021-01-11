"""
    Hadar Shahar
    The chat server code.
"""
import pickle
from tcp_network_protocol import create_packet
from custom_messages.chat_msg import ChatMsg
from server.broadcast_tcp_server import BroadcastTcpServer
from server.participant import Participant


class ChatServer(BroadcastTcpServer):
    """ Definition of the class ChatServer. """

    def __init__(self, ip: str, client_in_port: int, client_out_port: int):
        """ Constructor. """
        super(ChatServer, self).__init__(ip, client_in_port,
                                         client_out_port, 'chat')

    def handle_new_data(self, par: Participant, data: bytes):
        """
        Handles a given data that was received from a given participant.
        """
        msg = pickle.loads(data)
        # msg.add_timestamp()
        packet = create_packet(pickle.dumps(msg))

        if msg.recipient_id == ChatMsg.BROADCAST_ID:
            self.broadcast(par, packet)
        else:
            if msg.recipient_id in self.participants:
                # TODO maybe use sendall
                self.participants[msg.recipient_id].in_socket.send(packet)
