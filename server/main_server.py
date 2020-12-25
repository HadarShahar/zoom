"""
    Hadar Shahar
    The main server code.
"""
import sys

# add the parent directory to the "module search path"
# in order to import constants
sys.path.insert(0, '..')

from constants import *
from server.info_server import InfoServer
from server.broadcast_server import BroadcastServer
from server.chat_server import ChatServer

IP = '0.0.0.0'


class MainServer(object):
    """ Definition of the class MainServer. """

    def __init__(self, ip: str):
        """ Initializes the servers. """
        self.info_server = InfoServer(ip, CLIENT_IN_INFO_PORT,
                                      CLIENT_OUT_INFO_PORT)
        self.video_server = BroadcastServer(ip, CLIENT_IN_VIDEO_PORT,
                                            CLIENT_OUT_VIDEO_PORT, 'video')
        self.share_screen_server = BroadcastServer(ip, CLIENT_IN_SCREEN_PORT,
                                                   CLIENT_OUT_SCREEN_PORT,
                                                   'share_screen')
        self.audio_server = BroadcastServer(ip, CLIENT_IN_AUDIO_PORT,
                                            CLIENT_OUT_AUDIO_PORT, 'audio')
        self.chat_server = ChatServer(ip, CLIENT_IN_CHAT_PORT,
                                      CLIENT_OUT_CHAT_PORT)

        self.servers = (self.info_server, self.video_server,
                        self.share_screen_server, self.audio_server,
                        self.chat_server)

    def start(self):
        """ Starts the servers, each one in a separate thread. """
        for server in self.servers:
            server.start()


def main():
    """ Creates and Starts the main server. """
    server = MainServer(IP)
    server.start()


if __name__ == '__main__':
    main()
