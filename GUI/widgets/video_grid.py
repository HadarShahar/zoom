"""
    Hadar Shahar
    The video grid code.
"""
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from constants import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
from GUI.widgets.client_video_widget import ClientVideoWidget


class VideoGrid(QtWidgets.QFrame):
    """ Definition of the class VideoGrid. """

    def __init__(self, parent: QtWidgets.QWidget):
        """ Constructor. """
        super(VideoGrid, self).__init__(parent)
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.new_widgets_pos = ((0, 0), (0, 1), (1, 0), (1, 1))  # , (0, 2), (1, 2))
        self.widgets_counter = 0

    def add(self, video_widget: ClientVideoWidget) -> bool:
        """
        Adds a given ClientVideoWidget.
        :param video_widget: add this widget to the grid.
        :return: True if it was added, False otherwise.
        """
        if self.widgets_counter < len(self.new_widgets_pos):
            pos = self.new_widgets_pos[self.widgets_counter]
            self.layout.addWidget(video_widget, *pos)
            self.widgets_counter += 1
            self.update_widgets_size()
            return True

        print("can't add new video widget")
        return False

    def remove(self, video_widget: ClientVideoWidget):
        """ Removes a given ClientVideoWidget. """
        self.layout.removeWidget(video_widget)
        video_widget.deleteLater()

        self.widgets_counter -= 1
        self.update_widgets_size()

    def update_widgets_size(self):
        """ Updates the widgets size. """
        widgets = self.findChildren(ClientVideoWidget)
        maxw = self.width() // self.layout.columnCount()
        maxh = self.height() // self.layout.rowCount()

        # calc the maximum size with the original aspect ratio using an empty pixmap
        empty_pixmap = QPixmap(DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT)
        empty_pixmap = empty_pixmap.scaled(maxw, maxh, Qt.KeepAspectRatio)

        for w in widgets:
            w.setMaximumSize(empty_pixmap.size())

    def resizeEvent(self, event: QtGui.QResizeEvent):
        """
        This function is called when the grid is resized.
        It updates the widgets size.
        """
        self.update_widgets_size()
