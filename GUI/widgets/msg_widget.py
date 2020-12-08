"""
    Hadar Shahar

"""
from PyQt5 import QtWidgets
from chat_msg import ChatMsg


class MsgWidget(QtWidgets.QFrame):
    """ definition of the class MsgWidget """

    RECIPIENT_COLOR = 'blue'
    PRIVATELY_COLOR = 'red'

    def __init__(self, parent: QtWidgets.QWidget, msg: ChatMsg,
                 sender_name: str, recipient_name: str):
        """ constructor """
        super(MsgWidget, self).__init__(parent)

        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(5, 5, 10, 5)  # left, top, right, bottom
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        text = f'From {sender_name} to ' \
               f'<font color={MsgWidget.RECIPIENT_COLOR}>{recipient_name}</font>:'
        if msg.recipient_id != ChatMsg.BROADCAST_ID:
            text += f'<font color={MsgWidget.PRIVATELY_COLOR}>  (Privately)</font>'

        self.text_label = QtWidgets.QLabel(text, self)
        self.layout.addWidget(self.text_label, 0, 0)

        self.horizontal_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                       QtWidgets.QSizePolicy.Minimum)
        self.layout.addItem(self.horizontal_spacer, 0, 1)

        self.timestamp_label = QtWidgets.QLabel(msg.timestamp, self)
        self.layout.addWidget(self.timestamp_label, 0, 2)

        self.msg_text = QtWidgets.QLabel(msg.text, self)
        self.layout.addWidget(self.msg_text, 1, 0, 1, 2)  # row, column, row_span, column_span
