"""
    Hadar Shahar
    SmartBoardToolbar.
"""
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from GUI.smart_board.slider import Slider


class SmartBoardToolbar(QtWidgets.QFrame):
    """ Definition of the class SmartBoardToolbar. """

    HEIGHT = 50
    DEFAULT_PEN_COLOR = '#000000'  # black
    DEFAULT_PEN_WIDTH = 3
    new_color = pyqtSignal(str)

    def __init__(self, parent: QtWidgets.QWidget):
        """ Constructor. """
        super(SmartBoardToolbar, self).__init__(parent)

        self.pen_color = SmartBoardToolbar.DEFAULT_PEN_COLOR
        # self.pen_color = QColor(Qt.black)
        self.pen_width = SmartBoardToolbar.DEFAULT_PEN_WIDTH

        self.setFixedHeight(SmartBoardToolbar.HEIGHT)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addItem(self.default_hspacer())

        self.color_picker = QtWidgets.QPushButton(self)
        self.color_picker.setFixedSize(25, 25)
        self.color_picker.setStyleSheet(f'background-color: {self.pen_color};')
        self.color_picker.clicked.connect(self.pick_color)
        self.layout.addWidget(self.color_picker)

        self.pen_width_slider = Slider(self, 'pen width', 1, 5)
        self.pen_width_slider.value_changed.connect(self.set_pen_width)
        self.layout.addWidget(self.pen_width_slider)

        self.clear_button = QtWidgets.QPushButton('clear', self)
        self.layout.addWidget(self.clear_button)

        self.layout.addItem(self.default_hspacer())

    def pick_color(self):
        """
        This function is called when the color picker widget is clicked.
        It opens a dialog where the user can pick a color.
        Then it updates the selected color.
        """
        color = QtWidgets.QColorDialog.getColor()
        self.pen_color = color.name()
        self.color_picker.setStyleSheet(f'background-color: {self.pen_color};')
        self.new_color.emit(self.pen_color)

    def set_pen_width(self, value: int):
        """ Sets the pen width. """
        self.pen_width = value

    @staticmethod
    def default_hspacer() -> QtWidgets.QSpacerItem:
        """ Returns a new horizontal spacer item with the default values. """
        return QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                     QtWidgets.QSizePolicy.Minimum)
