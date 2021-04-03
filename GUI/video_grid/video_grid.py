"""
    Hadar Shahar
    The video grid code.
"""
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import numpy as np
from client.video.video_camera import VideoCamera
from client.video.basic_udp_video_client import BasicUdpVideoClient
from GUI.video_grid.client_video_widget import ClientVideoWidget
from network.custom_messages.client_info import ClientInfo


class VideoGrid(QtWidgets.QFrame):
    """ Definition of the class VideoGrid. """

    # the positions in the grid of the widgets that will be added
    NEW_WIDGETS_POS = ((0, 0), (0, 1), (1, 0), (1, 1))
    MAX_VIDEO_WIDGETS = len(NEW_WIDGETS_POS)

    def __init__(self, video_client: BasicUdpVideoClient,
                 parent: QtWidgets.QWidget):
        """ Constructor. """
        super(VideoGrid, self).__init__(parent)
        self.video_client = video_client
        self.video_client.frame_captured.connect(self.show_my_frame)
        self.video_client.frame_received.connect(self.show_video_frame)

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # {client_id: ClientVideoWidget(...)}
        self.video_widgets: [bytes, ClientVideoWidget] = {}

        # the video widgets, ordered by the time they were added to teh grid
        self.ordered_video_widgets: [ClientVideoWidget] = []

    def get_video_widget(self, client_id: bytes) -> ClientVideoWidget:
        """
        Returns the video widget that corresponds to
        the given client_id.
        """
        return self.video_widgets[client_id]

    def add_video_widget(self, client_info: ClientInfo) -> bool:
        """
        Creates a new ClientVideoWidget object and adds it to the grid.
        Returns True if it was added, False otherwise.
        """
        widgets_count = len(self.video_widgets)
        if widgets_count == VideoGrid.MAX_VIDEO_WIDGETS:
            print("can't add a new video widget")
            return False

        video_widget = ClientVideoWidget(self, client_info)
        self.video_widgets[client_info.id] = video_widget
        self.ordered_video_widgets.append(video_widget)

        pos = VideoGrid.NEW_WIDGETS_POS[widgets_count]
        self.layout.addWidget(video_widget, *pos)
        self.update_widgets_size()
        return True

    def remove_video_widget(self, client_id: bytes):
        """
        Removes the video widget of a client, given its id
        and rearranges the video grid.
        """
        video_widget = self.video_widgets[client_id]
        removed_widget_index = self.ordered_video_widgets.index(video_widget)
        self.layout.removeWidget(video_widget)
        video_widget.deleteLater()
        del self.video_widgets[client_id]

        # rearrange grid:
        for i in range(removed_widget_index + 1,
                       len(self.ordered_video_widgets)):
            w = self.ordered_video_widgets[i]
            new_pos = VideoGrid.NEW_WIDGETS_POS[i - 1]
            self.layout.removeWidget(w)
            self.layout.addWidget(w, *new_pos)

        self.ordered_video_widgets.pop(removed_widget_index)
        self.update_widgets_size()
        # for i in range(len(VideoGrid.NEW_WIDGETS_POS) - 1):
        #     pos = VideoGrid.NEW_WIDGETS_POS[i]
        #     # if there is a "hole" in the grid
        #     if not self.layout.itemAtPosition(*pos):
        #         next_pos = VideoGrid.NEW_WIDGETS_POS[i + 1]
        #         next_widget = self.layout.itemAtPosition(*next_pos)
        #         if next_widget:
        #             try:
        #                 self.layout.removeWidget(next_widget)
        #                 self.layout.addWidget(next_widget, *pos)
        #             except Exception as e:
        #                 print(e)

    def show_video_frame(self, frame: np.ndarray, client_id: bytes):
        """
        Receives a frame and the id of the client who sent it,
        and displays the frame in the matching video widget.
        """
        # the frame might be received after the client left,
        # and then its video widget isn't in self.video_widgets
        if client_id in self.video_widgets:
            self.video_widgets[client_id].show_frame(frame)

    def show_my_frame(self, frame: np.ndarray):
        """
        Receives a frame that was captured be this client and shows it.
        """
        self.show_video_frame(frame, self.video_client.id)

    def update_widgets_size(self):
        """ Updates the widgets size. """
        widgets = self.findChildren(ClientVideoWidget)
        maxw = self.width() // self.layout.columnCount()
        maxh = self.height() // self.layout.rowCount()

        # calc the maximum size with the original aspect ratio
        # using an empty pixmap
        empty_pixmap = QPixmap(VideoCamera.DEFAULT_VIDEO_WIDTH,
                               VideoCamera.DEFAULT_VIDEO_HEIGHT)
        empty_pixmap = empty_pixmap.scaled(maxw, maxh, Qt.KeepAspectRatio)

        for w in widgets:
            w.setMaximumSize(empty_pixmap.size())

    def resizeEvent(self, event: QtGui.QResizeEvent):
        """
        This function is called when the grid is resized.
        It updates the widgets size.
        """
        super(VideoGrid, self).resizeEvent(event)
        self.update_widgets_size()
