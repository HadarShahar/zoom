"""
    Hadar Shahar
    The main server code.
"""
from server.network_constants import *
from server.broadcast_udp_server import BroadcastUdpServer
from server.auth_server import AuthServer
from server.info_server import InfoServer
from server.chat_server import ChatServer

IP = '0.0.0.0'


class MainServer(object):
    """ Definition of the class MainServer. """

    def __init__(self, ip: str):
        """ Initializes the servers. """
        self.auth_server = AuthServer(AUTH_SERVER_PORT)
        client_id_validator = self.auth_server.validate_client_id

        self.info_server = InfoServer(
            ip, CLIENT_IN_INFO_PORT, CLIENT_OUT_INFO_PORT,
            self.client_disconnected, client_id_validator)
        self.chat_server = ChatServer(
            ip, CLIENT_IN_CHAT_PORT, CLIENT_OUT_CHAT_PORT, client_id_validator)

        self.video_server = BroadcastUdpServer(
            ip, CLIENT_IN_VIDEO_PORT, CLIENT_OUT_VIDEO_PORT,
            'video', client_id_validator)
        self.share_screen_server = BroadcastUdpServer(
            ip, CLIENT_IN_SCREEN_PORT, CLIENT_OUT_SCREEN_PORT,
            'share_screen', client_id_validator)
        self.audio_server = BroadcastUdpServer(
            ip, CLIENT_IN_AUDIO_PORT, CLIENT_OUT_AUDIO_PORT,
            'audio', client_id_validator)

        self.udp_servers = (self.video_server, self.share_screen_server,
                            self.audio_server)
        self.servers = (self.auth_server, self.info_server, self.chat_server,
                        *self.udp_servers)

    def start(self):
        """ Starts the servers, each one in a separate thread. """
        for server in self.servers:
            server.start()

    def client_disconnected(self, client_id: bytes):
        """
        The info server calls this function when a client disconnects.
        It informs all the udp clients, so they will remove this clients
        from their list of connected clients.
        It also informs the auth server so it will release its id.
        """
        for udp_server in self.udp_servers:
            udp_server.client_disconnected(client_id)
        self.auth_server.client_disconnected(client_id)


def main():
    """ Creates and Starts the main server. """
    server = MainServer(IP)
    server.start()


if __name__ == '__main__':
    main()
