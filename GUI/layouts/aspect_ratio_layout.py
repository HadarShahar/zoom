"""
    Hadar Shahar

"""
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np
import cv2
from constants import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT


class AspectRatioLayout(QtWidgets.QGridLayout):  # QLayoutItem
    """ definition of the class AspectRatioLayout """

    def __init__(self, parent: QtWidgets.QWidget):
        super(AspectRatioLayout, self).__init__(parent)
        self.ratio = DEFAULT_VIDEO_WIDTH / DEFAULT_VIDEO_HEIGHT

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, w: int) -> int:
        """
        Returns the preferred height for this layout item, given the width
        """
        val = super(AspectRatioLayout, self).heightForWidth(w)
        new_val = w * DEFAULT_VIDEO_HEIGHT // DEFAULT_VIDEO_WIDTH
        print(w, val, new_val)
        return new_val
