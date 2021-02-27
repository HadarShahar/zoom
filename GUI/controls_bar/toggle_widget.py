"""
    Hadar Shahar
    The toggle widget code.
"""
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal


class ToggleWidget(QtWidgets.QFrame):
    """ Definition of the class ToggleWidget. """

    WIDTH = 100
    HEIGHT = 50
    IMG_WIDTH = IMG_HEIGHT = 35

    LAYOUT_MARGINS = (0, 0, 0, 0)
    # this signal is emitted when this widget is clicked
    clicked = pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget, toggle_dict: dict,
                 is_on=True, toggle_onclick=True):
        """ Initializes the different widgets inside the ToggleWidget. """
        super(ToggleWidget, self).__init__(parent)
        self.toggle_dict = toggle_dict
        self.is_on = is_on
        self.toggle_onclick = toggle_onclick

        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(*ToggleWidget.LAYOUT_MARGINS)
        self.setLayout(self.layout)
        self.setFixedSize(ToggleWidget.WIDTH, ToggleWidget.HEIGHT)

        horizontal_layout = QtWidgets.QHBoxLayout()
        self.img = QtWidgets.QLabel()
        self.img.setFixedSize(ToggleWidget.IMG_WIDTH, ToggleWidget.IMG_HEIGHT)
        self.img.setScaledContents(True)
        self.img.setAlignment(Qt.AlignCenter)
        horizontal_layout.addWidget(self.img)
        self.layout.addLayout(horizontal_layout, 0, 0)

        self.label = QtWidgets.QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        # self.layout.addWidget(self.label, 1, 0)
        self.layout.addWidget(self.label)

        self.update()

    def update(self):
        """
        Updates the text and the image
        according to the widget state.
        """
        label_text, img_path = self.toggle_dict[self.is_on]
        self.label.setText(label_text)
        self.img.setPixmap(QtGui.QPixmap(img_path))

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """ This function is called when the mouse is pressed. """
        if self.toggle_onclick:
            self.toggle()
        self.clicked.emit()

    def toggle(self):
        """ Switches the state and updates the widget. """
        self.is_on = not self.is_on
        self.update()
