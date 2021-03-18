"""
    Hadar Shahar
    NotepadState.
"""


class NotepadState(object):
    """
    Definition of the class NotepadState.
    It represents a notepad window state.
    """

    def __init__(self, selection=(), text_len=0, lines_count=1):
        self.selection = selection
        self.text_len = text_len
        self.lines_count = lines_count
