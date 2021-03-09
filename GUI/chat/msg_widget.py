"""
    Hadar Shahar
    MsgWidget.
"""
from PyQt5 import QtWidgets
from network.custom_messages.chat_msg import ChatMsg
from GUI.gui_constants import DEFAULT_HSPACER_SIZE


class MsgWidget(QtWidgets.QFrame):
    """ Definition of the class MsgWidget. """

    RECIPIENT_COLOR = 'blue'
    PRIVATELY_COLOR = 'red'

    LAYOUT_MARGINS = (5, 5, 10, 5)  # left, top, right, bottom
    LAYOUT_SPACING = 0  # no spacing between widgets

    # row, column, row_span, column_span
    MSG_TEXT_LAYOUT_POSITION = (1, 0, 1, 2)

    def __init__(self, parent: QtWidgets.QWidget, msg: ChatMsg,
                 sender_name: str, recipient_name: str):
        """ Constructor. """
        super(MsgWidget, self).__init__(parent)

        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(*MsgWidget.LAYOUT_MARGINS)
        self.layout.setSpacing(MsgWidget.LAYOUT_SPACING)
        self.setLayout(self.layout)

        text = f'From {sender_name} to ' \
               f'<font color={MsgWidget.RECIPIENT_COLOR}>' \
               f'{recipient_name}</font>:'
        if msg.recipient_id != ChatMsg.BROADCAST_ID:
            text += f'<font color={MsgWidget.PRIVATELY_COLOR}>  ' \
                    f'(Privately)</font>'

        self.text_label = QtWidgets.QLabel(text, self)
        self.layout.addWidget(self.text_label, 0, 0)

        self.horizontal_spacer = QtWidgets.QSpacerItem(
            *DEFAULT_HSPACER_SIZE, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum)
        self.layout.addItem(self.horizontal_spacer, 0, 1)

        self.timestamp_label = QtWidgets.QLabel(msg.timestamp, self)
        self.layout.addWidget(self.timestamp_label, 0, 2)

        self.msg_text = QtWidgets.QLabel(msg.text, self)
        self.layout.addWidget(self.msg_text,
                              *MsgWidget.MSG_TEXT_LAYOUT_POSITION)
