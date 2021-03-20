"""
    Hadar Shahar
    Remote window message.
"""


class RemoteWindowMsg(object):
    """ Definition of the class RemoteWindowMsg. """

    # messages types
    SET_SELECTION = 1  # data = (start_index: int, end_index: int)
    REPLACE_LINE = 2   # data = (line_index: int, new_line: str)
    SET_TEXT = 3       # data = (text: str,)

    def __init__(self, msg_type: int, data: tuple):
        """ Constructor. """
        self.type = msg_type
        self.data = data

    def __repr__(self) -> str:
        """ Returns the RemoteWindowMsg attributes. """
        return str(self.__dict__)
