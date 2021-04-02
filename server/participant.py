"""
    Hadar Shahar
    Participant.
"""
import threading


class Participant(object):
    """ Definition of the class Participant. """

    def __init__(self, address: (str, int), in_socket=None, out_socket=None,
                 meeting_id=b'', client_id=b''):
        """ Constructor. """
        self.address = address
        self.in_socket = in_socket
        self.out_socket = out_socket
        self.meeting_id = meeting_id
        self.client_id = client_id
        self.lock = threading.Lock()

        # client_info is only used by the info server
        self.client_info = None

    def done_connecting(self) -> bool:
        """
        Checks if the participant has connected to the server
        via input and output sockets.
        """
        return None not in (self.in_socket, self.out_socket)

    def close_sockets(self):
        """ Closes the participant's sockets. """
        self.in_socket.close()
        self.out_socket.close()

    # def __eq__(self, other) -> bool:
    #     """
    #     Checks if a given participant has the same ids as this participant.
    #     This function is necessary for removing a Participant object
    #     from a list of participants using list.remove().
    #     """
    #     return self.meeting_id == other.meeting_id and \
    #         self.client_id == other.client_id

    def __repr__(self) -> str:
        """ Returns the participant representation. """
        # return f'Par(id={self.id})'
        return f'Par({self.address})'
