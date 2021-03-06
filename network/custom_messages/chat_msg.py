"""
    Hadar Shahar
    Chat message.
"""
import datetime


class ChatMsg(object):
    """ Definition of the class ChatMsg. """
    BROADCAST_ID = b'*'
    BROADCAST_NAME = 'Everyone'

    def __init__(self, sender_id: bytes, recipient_id: bytes, text: str):
        """ Constructor. """
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.text = text
        self.timestamp = ''

    def add_timestamp(self):
        """ Adds a timestamp to the message."""
        now = datetime.datetime.now()
        self.timestamp = f'{now.hour:02}:{now.minute:02}'  # pad to 2 digits

    def __repr__(self) -> str:
        """ Returns the message representation. """
        return f'ChatMsg({self.__dict__})'
