"""
    Hadar Shahar
    The chat recipients code.
"""
from PyQt5 import QtGui
from custom_messages.chat_msg import ChatMsg


class ChatRecipients(QtGui.QStandardItemModel):
    """
    Definition of the class ChatRecipients
    this class represents the model of the chat recipient combo box.

    This model contains the id and the name of each client in the meeting,
    it is used for selecting a chat recipient.
    """

    def __init__(self, client_id: bytes):
        super(ChatRecipients, self).__init__()
        self.client_id = client_id

        self.recipients = {}  # {recipient_id: recipient_name}

        # add a broadcast recipient
        self.add(ChatMsg.BROADCAST_ID, ChatMsg.BROADCAST_NAME)

    def add(self, recipient_id: bytes, recipient_name: str):
        """ Adds a recipient. """
        self.recipients[recipient_id] = recipient_name
        item = QtGui.QStandardItem(recipient_name)
        item.setData(recipient_id)
        self.appendRow(item)

    def remove(self, recipient_id: bytes):
        """ Removes a recipient. """
        del self.recipients[recipient_id]
        for i in range(self.rowCount()):
            if self.item(i).data() == recipient_id:
                self.removeRow(i)
                return

    def get_name(self, recipient_id: bytes) -> str:
        """ Returns the recipient name, given its id. """
        if recipient_id == self.client_id:
            return 'Me'
        return self.recipients[recipient_id]
        # for i in range(self.rowCount()):
        #     if self.item(i).data() == recipient_id:
        #         return self.item(i).text()
