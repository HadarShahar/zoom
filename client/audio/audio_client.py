"""
    Hadar Shahar
    The audio client code.
"""
from network_protocol import send_packet, recv_packet
from client.basic_client import BasicClient
from client.audio.audio_stream import AudioStream


class AudioClient(BasicClient):
    """ Definition of the class AudioClient. """

    def __init__(self, ip: str, in_socket_port: int, out_socket_port: int,
                 client_id: bytes):
        """ Constructor. """
        super(AudioClient, self).__init__(ip, in_socket_port, out_socket_port,
                                          client_id)
        self.stream = AudioStream(input=True, output=True)

    def send_data_loop(self):
        """
        Reads audio from the AudioStream (in chunks)
        and sends each chunk to the server.
        """
        while self.running and self.is_sharing:
            chunk = self.stream.read_chunk()
            if not self.stream.is_silent(chunk):
                send_packet(self.out_socket, chunk)

    def receive_data_loop(self):
        """
        Receives each audio chunk from the server
        and writes it to an output stream (plays it).
        """
        while self.running:
            # convert to bytes because bytearray is
            # unhashable => can't be a dictionary key
            sender_id = bytes(recv_packet(self.in_socket))

            # can only write a bytes-like object to audio stream(not bytearray)
            data = bytes(recv_packet(self.in_socket))
            self.stream.write(data)
