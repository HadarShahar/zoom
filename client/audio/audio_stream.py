"""
    Hadar Shahar
    AudioStream.
"""
import pyaudio
import wave
from array import array
import threading


class AudioStream(object):
    """ Definition of the class AudioStream. """

    CHUNK = 1024              # record in chunks of 1024 samples
    FORMAT = pyaudio.paInt16  # 16 bits per sample
    CHANNELS = 1              # this value is 2 in the documentation example
    RATE = 44100              # record at 44100 samples per second

    # if the max number in a chunk is less than this threshold,
    # this chunk is considered silent
    SILENT_THRESHOLD = 500

    def __init__(self, input=True, output=True):
        """ Constructor. """
        self.p = pyaudio.PyAudio()

        # pyaudio.paInt16 = self.p.get_format_from_width(2) = 8
        self.stream = self.p.open(format=AudioStream.FORMAT,
                                  channels=AudioStream.CHANNELS,
                                  rate=AudioStream.RATE,
                                  input=input,
                                  output=output,
                                  frames_per_buffer=AudioStream.CHUNK)
        print('Connected to audio')
        self.lock = threading.Lock()
        self.is_open = True

    def read_chunk(self) -> bytes:
        """ Reads a chunk from the stream. """
        with self.lock:
            if self.is_open:
                return self.stream.read(AudioStream.CHUNK)
            return b''

    def write(self, data: bytes):
        """ Writes data to the stream. """
        with self.lock:
            if self.is_open:
                self.stream.write(data)

    def close_stream(self):
        """ Closes the stream (called in a new thread). """
        with self.lock:
            try:
                self.stream.stop_stream()
            except OSError:
                pass  # The stream is not open
            finally:
                self.stream.close()
                self.p.terminate()
                print(f'Closed stream.')

    def close(self):
        """ Closes the stream. """
        self.is_open = False
        threading.Thread(target=self.close_stream).start()

    @staticmethod
    def is_silent(data: bytes) -> bool:
        """
        Checks if a given chunk of data is silent.
        """
        if data == b'':
            return True
        # convert the data to array of signed shorts (closer to 0 is quieter)
        data = array('h', data)
        return max(data) < AudioStream.SILENT_THRESHOLD


# ==================================================================== testing

def record_and_play():
    stream = AudioStream()
    while True:
        chunk = stream.read_chunk()
        stream.write(chunk)


def play_from_files():
    stream = AudioStream()
    wf1 = None
    wf2 = None
    file_data1 = b''
    while True:
        if file_data1 == b'':
            print('playing again')
            wf1 = wave.open('../../playground/output1.wav', 'rb')
            wf2 = wave.open('../../playground/output2.wav', 'rb')
        file_data1 = wf1.readframes(AudioStream.CHUNK)
        stream.write(file_data1)
        stream.write(wf2.readframes(AudioStream.CHUNK))


if __name__ == '__main__':
    try:
        record_and_play()
        # play_from_files()
    except Exception as ex:
        print(ex)

    print('end')
