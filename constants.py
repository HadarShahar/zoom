"""
    Hadar Shahar
    constants file
"""

# the parameter for socket.listen()
NUMBER_OF_WAITING_CONNECTIONS = 100

# the VideoCapture image size
DEFAULT_VIDEO_WIDTH = 640
DEFAULT_VIDEO_HEIGHT = 480
DIVIDER = 1
VIDEO_WIDTH = DEFAULT_VIDEO_WIDTH / DIVIDER
VIDEO_HEIGHT = DEFAULT_VIDEO_HEIGHT / DIVIDER

# the quality of the image from 0 to 100 (the higher is the better)
JPEG_QUALITY = 80  # default is 95

# MSG_LEN = 4  # 8
CHUNK_SIZE = 1024
EOF = b'-1'
EXIT_SIGN = b'EXIT'


# '>' for big-endian (network byte order is always big-endian)
# 'I' for unsigned int which takes 4 bytes
NETWORK_BYTES_FORMAT = '>I'
# The number of bytes each number takes (according to NETWORK_BYTES_FORMAT)
NETWORK_BYTES_PER_NUM = 4

# "For best match with hardware and network realities, the value of bufsize
# should be a relatively small power of 2, for example, 4096."
UDP_SOCKET_BUFFER_SIZE = 4096

# when a udp client connects to the meeting, it sends this message
# to the udp server to inform it that it has connected
UDP_NEW_CLIENT_MSG = b'HELLO'


# from enum import Enum
# class Info(Enum):
class Info:
    """
    Valid info messages:

    message name         , message data
    ================================================================================================
    NEW_CLIENT           , ClientInfo(...)
    CLIENTS_INFO         , [ClientInfo(...), ... ]
    CLIENT_LEFT          , client_id: bytes

    TOGGLE_AUDIO         , client_id: bytes
    TOGGLE_VIDEO         , client_id: bytes

    START_SCREEN_SHARING , client_id: bytes
    STOP_SCREEN_SHARING  , client_id: bytes

    START_PAINTING       , client_id: bytes
    STOP_PAINTING        , client_id: bytes
    NEW_PAINTING         , Painting(...)

    START_REMOTE_WINDOW  , client_id: bytes
    STOP_REMOTE_WINDOW   , client_id: bytes
    REMOTE_WINDOW_MSG    , RemoteWindowMsg(...)
    """
    NEW_CLIENT = 1
    CLIENTS_INFO = 2
    CLIENT_LEFT = 3

    TOGGLE_AUDIO = 4
    TOGGLE_VIDEO = 5

    START_SCREEN_SHARING = 6
    STOP_SCREEN_SHARING = 7

    START_PAINTING = 8
    STOP_PAINTING = 9
    NEW_PAINTING = 10

    START_REMOTE_WINDOW = 11
    STOP_REMOTE_WINDOW = 12
    REMOTE_WINDOW_MSG = 13

    OPPOSITE_MSGS = {
        START_SCREEN_SHARING: STOP_SCREEN_SHARING,
        START_PAINTING: STOP_PAINTING,
        START_REMOTE_WINDOW: STOP_REMOTE_WINDOW
    }
