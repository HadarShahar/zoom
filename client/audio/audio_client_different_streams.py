"""
    Hadar Shahar

"""
from client.basic_client import BasicClient
from client.audio.audio_stream import AudioStream
from network_protocol import send_packet, recv_packet


class AudioClient(BasicClient):
    """ definition of the class AudioClient """

    def __init__(self, ip, in_socket_port, out_socket_port):
        """
        """
        super(AudioClient, self).__init__(ip, in_socket_port, out_socket_port)

    def send_data_loop(self):
        """
        reads audio from the AudioStream (in chunks)
        and sends each chunk to the server
        """
        try:
            stream = AudioStream(input=True, output=False)
            print('Connected to audio')
            while True:
                data = stream.read_chunk()
                send_packet(self.out_socket, data)
        except Exception as e:
            print('AudioClient send_data_loop:', e)
            self.close()

    def receive_data_loop(self):
        """
        receives each audio chunk from the server
        and writes it to an output stream (plays it)
        """
        try:
            output_streams: [bytes, AudioStream] = {}
            # {client id: output stream of data received from the client}

            while True:
                # bytearray is unhashable => can't be a dictionary key
                sender_id = bytes(recv_packet(self.in_socket))
                # can't write bytearray object to audio stream (a bytes-like object is required)
                data = bytes(recv_packet(self.in_socket))

                if sender_id in output_streams:
                    output_streams[sender_id].write(data)
                else:
                    output_streams[sender_id] = AudioStream(input=False, output=True)

        except Exception as e:
            print('AudioClient receive_data_loop:', e)
            self.close()
