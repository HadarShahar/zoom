"""
    Hadar Shahar
    Participant.
"""
import threading


class Participant(object):
    """ definition of the class Participant """

    def __init__(self, address: (str, int), in_socket=None, out_socket=None, par_id=b'',
                 name='', is_audio_on=True, is_video_on=True):
        """ constructor """
        self.address = address
        self.in_socket = in_socket
        self.out_socket = out_socket
        self.id = par_id  # in bytes
        self.lock = threading.Lock()

        # these are only used by the info server
        self.name = name
        self.is_audio_on = is_audio_on
        self.is_video_on = is_video_on

    def get_info(self) -> tuple:
        """
        returns the info that the info server needs
        """
        return self.id, self.name, self.is_audio_on, self.is_video_on

    def done_connecting(self) -> bool:
        """
        checks if the participant has connected to the server
        via input and output sockets.
        """
        return None not in (self.in_socket, self.out_socket)

    def close_sockets(self):
        """ closes the participant's sockets """
        self.in_socket.close()
        self.out_socket.close()

    def __eq__(self, other) -> bool:
        """ checks if a given participant has the same address as this participant """
        return self.address == other.address

    def __repr__(self) -> str:
        """ returns the participant representation """
        return f'Par(id={self.id})'
