import os
import random
import requests
import urllib.parse
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, send_file
from dotenv import load_dotenv

# configure it at: https://www.twilio.com/console/sms/whatsapp/sandbox
NGROK_URL = 'https://57ca878d.ngrok.io'


# print(f'https://wa.me/{WHATSAPP_SANDBOX_NUMBER}?text='
#       f'{urllib.parse.quote(JOIN_SANDBOX_MESSAGE)}')
# https://wa.me/14155238886?text=join%20foreign-captured


class WhatsappBotServer(object):
    WHATSAPP_NUMBER_PREFIX = 'whatsapp:+'
    # NOTE: this template can't be changed
    # because it's one of the pre-registered messages for twilio sandbox
    LOGIN_CODE_MSG_TEMPLATE = 'Your {} code is {}'

    def __init__(self, name: str):
        """ Constructor. """
        super(WhatsappBotServer, self).__init__()
        load_dotenv()
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.twilio_client = Client(account_sid, auth_token)

        self.whatsapp_number = '14155238886'
        # because I use a free trial account, new users must send this message
        # to the sandbox number in order to join the sandbox
        self.msg_to_join_sandbox = 'join foreign-captured'

        self.app = Flask(name)
        self.app.add_url_rule('/msg', None, self.msg_reply, methods=['POST'])

    def run(self):
        """ Runs the server. """
        self.app.run(debug=True)

    def msg_reply(self):
        """ Respond to incoming messages. """
        resp = MessagingResponse()

        print(request.values)

        body = request.values.get('Body', None)
        sender_num = request.values.get('From')\
            .replace(self.WHATSAPP_NUMBER_PREFIX, '')

        return str(resp)

    def send_msg(self, body: str, recipient_number: str):
        message = self.twilio_client.messages.create(
            body=body,
            from_=self.WHATSAPP_NUMBER_PREFIX + self.whatsapp_number,
            to=self.WHATSAPP_NUMBER_PREFIX + recipient_number
        )
        print(message.sid)


if __name__ == "__main__":
    server = WhatsappBotServer(__name__)
    server.run()
