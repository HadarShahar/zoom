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
        self.in_stream = AudioStream(input=True, output=False)
        self.out_stream = AudioStream(input=False, output=True)

    def send_data_loop(self):
        """
        Reads audio from the AudioStream (in chunks)
        and sends each chunk to the server.
        """
        while self.running and self.is_sharing:
            try:
                chunk = self.in_stream.read_chunk()
            except OSError as e:
                # [Errno -9999] Unanticipated host error
                # might happen if someone disconnects the connected headphones
                print('AudioClient.send_data_loop:', e)
                self.in_stream.close()
                print('Recreating the input stream...')
                self.in_stream = AudioStream(input=True, output=False)
                continue
            if not AudioStream.is_silent(chunk):
                self.send_data(chunk)

    def receive_data_loop(self):
        """
        Receives each audio chunk from the server
        and writes it to an output stream (plays it).
        """
        while self.running:
            sender_id, data = self.receive_data()
            if data is not None:
                try:
                    self.out_stream.write(data)
                except OSError as e:
                    # [Errno -9999] Unanticipated host error
                    # occurs if 2 clients are running on the same computer
                    # recreating the stream fixes it
                    print('AudioClient.receive_data_loop:', e)
                    self.out_stream.close()
                    print('Recreating the stream...')
                    self.out_stream = AudioStream(input=False, output=True)

    def close(self):
        """ Closes the streams. """
        super(AudioClient, self).close()
        self.in_stream.close()
        self.out_stream.close()
