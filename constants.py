"""
    Hadar Shahar
    constants file
"""

# import the server ip and the ports
from registry_constants import *

# the parameter for socket.listen()
NUMBER_OF_WAITING_CONNECTIONS = 100

# the VideoCapture image size
DEFAULT_VIDEO_WIDTH = 640
DEFAULT_VIDEO_HEIGHT = 480
DIVIDER = 1
VIDEO_WIDTH = DEFAULT_VIDEO_WIDTH / DIVIDER
VIDEO_HEIGHT = DEFAULT_VIDEO_HEIGHT / DIVIDER

# the quality of the image from 0 to 100 (the higher is the better)
JPEG_QUALITY = 50  # default is 95

MSG_LEN = 4  # 8
CHUNK_SIZE = 1024
EOF = b'-1'
EXIT_SIGN = b'EXIT'


# from enum import Enum
# class Info(Enum):
class Info:
    """
    valid info messages

    message name         , message data
    ================================================================================================
    NEW_CLIENT           , (client_id: bytes, client_name: str, is_audio_on: bool, is_video_on: bool)
    CLIENTS_INFO         , [(client_id: bytes, client_name: str, is_audio_on: bool, is_video_on: bool),...]
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
