"""
    Hadar Shahar
    The basic video widget code.
"""
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np
import cv2
from client.video.video_camera import VideoCamera


class BasicVideoWidget(QtWidgets.QLabel):
    """ Definition of the class BasicVideoWidget. """

    SIZE_DIVIDER = 4
    MIN_WIDTH = VideoCamera.DEFAULT_VIDEO_WIDTH // SIZE_DIVIDER
    MIN_HEIGHT = VideoCamera.DEFAULT_VIDEO_HEIGHT // SIZE_DIVIDER

    def __init__(self, parent: QtWidgets.QWidget):
        """ Constructor. """
        super(BasicVideoWidget, self).__init__(parent)

        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.setAlignment(Qt.AlignCenter)

    def show_frame(self, frame: np.ndarray):
        """
        Receives a cv2 image (numpy array),
        converts it to QPixmap and shows it.
        """
        pixmap = self.convert_cv2pixmap(frame)
        self.setPixmap(pixmap)

    def convert_cv2pixmap(self, cv_img: np.ndarray, scale=True) -> QPixmap:
        """ Converts an opencv image to QPixmap. """
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape

        q_img = QImage(rgb_image, w, h, QImage.Format_RGB888)
        if scale:
            q_img = q_img.scaled(self.width(), self.height(),
                                 Qt.KeepAspectRatio)
        return QPixmap.fromImage(q_img)
