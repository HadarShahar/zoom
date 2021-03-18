"""
    Hadar Shahar
    RemoteWindowContainer.
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from GUI.widgets.basic_video_widget import BasicVideoWidget
from GUI.win32.remote_notepad import RemoteNotepad


class RemoteWindowContainer(QtWidgets.QWidget):
    """ Definition of the class RemoteWindowContainer. """

    # the number of pixels between the remote window and its container
    PADDING = 7

    def __init__(self, parent: QtWidgets.QWidget):
        """ Constructor. """
        super(RemoteWindowContainer, self).__init__(parent)
        self.remote_window = RemoteNotepad()
        self.main_window_pos = QtCore.QPoint()

        # test for resizing in the beginning
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.label = QtWidgets.QLabel(self)
        self.label.setMinimumSize(BasicVideoWidget.MIN_WIDTH,
                                  BasicVideoWidget.MIN_HEIGHT)
        self.layout.addWidget(self.label)

    def set_main_window_pos(self, pos: QtCore.QPoint):
        """ Sets the main window position. """
        self.main_window_pos = pos
        self.update_remote_window()

    def show(self):
        """ Show the container and creates the remote window. """
        super(RemoteWindowContainer, self).show()
        self.remote_window.create_window()
        self.remote_window.start()
        self.update_remote_window()

    def hide(self):
        """ Hides the container and closes the remote window. """
        super(RemoteWindowContainer, self).hide()
        self.remote_window.close()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        """
        This function is called when this widget is resized.
        It updates the remote window size.
        """
        super(RemoteWindowContainer, self).resizeEvent(event)
        self.update_remote_window()

    def update_remote_window(self):
        """ Updates the remote window size and position. """
        if self.remote_window.is_open:
            x = self.main_window_pos.x() + self.x() - self.PADDING
            y = self.main_window_pos.y() + self.y() + self.PADDING
            w = self.width() + 2 * self.PADDING
            h = self.height() + self.PADDING
            self.remote_window.set_window_pos(x, y, w, h)
