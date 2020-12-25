"""
    Hadar Shahar.
    GUI constants.
"""

STYLE_SHEET_PATH = 'stylesheet.qss'
PATH_TO_IMAGES = 'images'
TOGGLE_AUDIO_DICT = {
    True: ('Mute', f'{PATH_TO_IMAGES}/open_mic.png'),
    False: ('Unmute', f'{PATH_TO_IMAGES}/closed_mic.png')
}
TOGGLE_VIDEO_DICT = {
    True: ('Stop Video', f'{PATH_TO_IMAGES}/open_camera.png'),
    False: ('Start Video', f'{PATH_TO_IMAGES}/closed_camera.png')
}

TOGGLE_CHAT_PROPERTIES = ('Chat', f'{PATH_TO_IMAGES}/chat_icon.png')
# the chat widget looks the same when it's on/off
TOGGLE_CHAT_DICT = {
    True: TOGGLE_CHAT_PROPERTIES,
    False: TOGGLE_CHAT_PROPERTIES
}

TOGGLE_SHARE_SCREEN_DICT = {
    True: ('Stop Share', f'{PATH_TO_IMAGES}/stop_icon.png'),
    False: ('Share Screen', f'{PATH_TO_IMAGES}/share_screen_icon.png')
}

TOGGLE_SMART_BOARD_DICT = {
    True: ('Close Board', f'{PATH_TO_IMAGES}/stop_icon.png'),
    False: ('Smart Board', f'{PATH_TO_IMAGES}/board_icon.png')
}

TOGGLE_REMOTE_WINDOW_DICT = {
    True: ('Close Window', f'{PATH_TO_IMAGES}/stop_icon.png'),
    False: ('Remote Window', f'{PATH_TO_IMAGES}/windows_icon.png')
}

