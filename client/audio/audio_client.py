"""
    Hadar Shahar
    The audio client code.
"""
from client.network_constants import Constants
from client.basic_udp_client import BasicUdpClient
from client.audio.audio_stream import AudioStream


class AudioClient(BasicUdpClient):
    """ Definition of the class AudioClient. """

    def __init__(self, client_id: bytes):
        """ Constructor. """
        super(AudioClient, self).__init__(
            Constants.SERVER_IP, Constants.CLIENT_IN_AUDIO_PORT,
            Constants.CLIENT_OUT_AUDIO_PORT, client_id)
        self.stream = AudioStream(input=True, output=True)

    def send_data_loop(self):
        """
        Reads audio from the AudioStream (in chunks)
        and sends each chunk to the server.
        """
        while self.running and self.is_sharing:
            chunk = self.stream.read_chunk()
            if not self.stream.is_silent(chunk):
                self.send_data(chunk)

    def receive_data_loop(self):
        """
        Receives each audio chunk from the server
        and writes it to an output stream (plays it).
        """
        while self.running:
            sender_id, data = self.receive_data()
            if data is not None:
                self.stream.write(data)
