"""
    Hadar Shahar
    General info messages.
"""


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
