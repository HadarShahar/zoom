"""
    Hadar Shahar
    The controls bar frame.
"""
from PyQt5 import QtWidgets
from GUI.controls_bar.toggle_widget import ToggleWidget
from GUI.gui_constants import *


class ControlsBarFrame(QtWidgets.QFrame):
    """ Definition of the class ControlsBarFrame. """

    HEIGHT = 55
    LEAVE_BTN_SIZE = (60, 25)  # width, height
    LAYOUT_MARGINS = (0, 0, 10, 0)  # left, top, right, bottom
    LAYOUT_SPACING = 0  # no spacing between widgets

    def __init__(self, parent: QtWidgets.QWidget,
                 is_audio_on: bool, is_video_on: bool):
        """ Constructor. """
        super(ControlsBarFrame, self).__init__(parent)
        self.is_audio_on = is_audio_on
        self.is_video_on = is_video_on

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Preferred)
        self.setSizePolicy(size_policy)
        self.setFixedHeight(ControlsBarFrame.HEIGHT)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(*ControlsBarFrame.LAYOUT_MARGINS)
        self.layout.setSpacing(ControlsBarFrame.LAYOUT_SPACING)

        self.create_toggles()
        default_hspacer = QtWidgets.QSpacerItem(
            *DEFAULT_HSPACER_SIZE, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.layout.addItem(default_hspacer)

        self.leave_button = QtWidgets.QPushButton('Leave', self)
        self.leave_button.setFixedSize(*ControlsBarFrame.LEAVE_BTN_SIZE)
        self.leave_button.setObjectName('leave_button')
        self.layout.addWidget(self.leave_button)

    def create_toggles(self):
        """
        Creates the toggle widgets for
        audio, video, chat, share screen, smart board and remote window.
        """
        self.toggle_audio_widget = ToggleWidget(
            self, TOGGLE_AUDIO_DICT, is_on=self.is_audio_on)

        self.toggle_video_widget = ToggleWidget(
            self, TOGGLE_VIDEO_DICT, is_on=self.is_video_on)

        self.toggle_chat_widget = ToggleWidget(
            self, TOGGLE_CHAT_DICT, is_on=False)

        self.toggle_share_screen_widget = ToggleWidget(
            self, TOGGLE_SHARE_SCREEN_DICT, is_on=False, toggle_onclick=False)

        self.toggle_smart_board_widget = ToggleWidget(
            self, TOGGLE_SMART_BOARD_DICT, is_on=False, toggle_onclick=False)

        self.toggle_remote_window_widget = ToggleWidget(
            self, TOGGLE_REMOTE_WINDOW_DICT, is_on=False, toggle_onclick=False)

        # add all the toggle widgets to the controls bar layout
        widgets = (self.toggle_audio_widget, self.toggle_video_widget,
                   self.toggle_chat_widget, self.toggle_share_screen_widget,
                   self.toggle_smart_board_widget,
                   self.toggle_remote_window_widget)
        for widget in widgets:
            self.layout.addWidget(widget)
