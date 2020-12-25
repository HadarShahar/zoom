"""
    Hadar Shahar
    Painting.
"""


class Painting(object):
    """ Definition of the class Painting. """

    # painting types
    LINE = 1          # data = (x1, y1, x2, y2)
    CLEAR_POINTS = 2  # data = [(x1, y1), (x2, y2), ...]
    RECTANGLE = 3     # data = (x, y ,w, h)
    CLEAR_ALL = 4     # data = None

    def __init__(self, painting_type: int, data=None,
                 pen_color: str = None, pen_width: int = None):
        """ Constructor. """
        self.type = painting_type
        self.data = data
        self.pen_color = pen_color
        self.pen_width = pen_width

    def __repr__(self) -> str:
        """ Returns the painting attributes. """
        return str(self.__dict__)
