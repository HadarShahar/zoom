"""
    Hadar Shahar

"""
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSignal
import requests
import threading
import numpy as np
import cv2
from GUI.widgets.basic_video_widget import BasicVideoWidget
from custom_messages.client_info import ClientInfo


class ClientVideoWidget(BasicVideoWidget):
    """ Definition of the class ClientVideoWidget. """

    BORDER_SIZE = 3
    NO_BORDER_STYLE = 'border: none;'
    BORDER_STYLE = f'border: {BORDER_SIZE}px solid blue;'
    SPEAKER_BORDER_STYLE = f'border: {BORDER_SIZE}px solid yellow;'

    IMG_WIDTH = IMG_HEIGHT = 20
    RED_MIC_PATH = 'images/red_mic.png'  # TODO path to images

    def __init__(self, parent: QtWidgets.QWidget, client_info: ClientInfo):
        """ Initializes the different widgets inside the ClientVideoWidget. """
        super(ClientVideoWidget, self).__init__(parent)

        self.client_info = client_info
        self.is_audio_on = client_info.is_audio_on
        self.is_video_on = client_info.is_video_on

        self.default_img_pixmap = None
        if client_info.img_url:
            threading.Thread(target=self.download_default_img,
                             args=(client_info.img_url,)).start()

        # size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
        # QtWidgets.QSizePolicy.Preferred)
        # size_policy.setHeightForWidth(True)
        # self.setSizePolicy(size_policy)

        self.setStyleSheet(self.BORDER_STYLE)
        self.setText(self.client_info.name)

        self.bottom_frame = QtWidgets.QFrame(self)
        self.bottom_frame.setMinimumSize(self.IMG_WIDTH, self.IMG_HEIGHT)
        self.bottom_frame.setStyleSheet(self.NO_BORDER_STYLE)

        horizontal_layout = QtWidgets.QHBoxLayout()
        horizontal_layout.setContentsMargins(0, 0, 0,
                                             0)  # left, top, right, bottom
        horizontal_layout.setSpacing(0)
        self.red_mic = QtWidgets.QLabel(self.bottom_frame)
        self.red_mic.setPixmap(QPixmap(self.RED_MIC_PATH))
        self.red_mic.setFixedSize(self.IMG_WIDTH, self.IMG_HEIGHT)
        self.red_mic.setScaledContents(True)
        horizontal_layout.addWidget(self.red_mic)

        self.name_label = QtWidgets.QLabel(f'  {self.client_info.name}  ',
                                           self.bottom_frame)
        horizontal_layout.addWidget(self.name_label)
        self.bottom_frame.setLayout(horizontal_layout)

        self.update_bottom_label()

    def show_frame(self, frame: np.ndarray):
        """ Shows the frame if needed. """
        if self.is_video_on:
            super(ClientVideoWidget, self).show_frame(frame)

    def toggle_audio(self):
        """ Turns on/off the audio. """
        self.is_audio_on = not self.is_audio_on
        self.update_bottom_label()

    def toggle_video(self):
        """ Turns on/off the video. """
        self.is_video_on = not self.is_video_on
        self.update_bottom_label()

    def update_bottom_label(self):
        """
        Hides or shows the name label and the red microphone image
        at the bottom of the widget according to
        is_audio_on and is_video_on.
        """
        if self.is_audio_on and not self.is_video_on and \
                self.default_img_pixmap is None:
            self.bottom_frame.hide()
        else:
            self.bottom_frame.show()

        if self.is_audio_on:
            self.red_mic.hide()
        else:
            self.red_mic.show()

        if self.is_video_on:
            self.name_label.show()
        else:
            if self.default_img_pixmap is None:
                self.name_label.hide()
                self.setText(self.client_info.name)
            else:
                self.setPixmap(self.default_img_pixmap)

        self.bottom_frame.adjustSize()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        """
        This function is called when the widget is resized.
        It moves the bottom frame to the bottom of the widget.
        """
        # p = QPixmap(DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT)
        # p = p.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        # print(p.size(), self.size())

        self.bottom_frame.move(self.BORDER_SIZE,
                               self.height()-self.IMG_HEIGHT-self.BORDER_SIZE)

    def download_default_img(self, url: str):
        content = requests.get(url).content
        nparr = np.frombuffer(content, dtype=np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        self.default_img_pixmap = self.convert_cv2pixmap(frame, scale=False)
