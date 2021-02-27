"""
    Hadar Shahar
    AuthServer.
"""
import os
import threading
import requests
from flask import Flask, request
from dotenv import load_dotenv


class AuthServer(threading.Thread):
    """ Definition of the class AuthServer. """

    GOOGLE_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
    GOOGLE_USER_INFO_ENDPOINT = \
        'https://www.googleapis.com/oauth2/v3/userinfo?access_token={}'

    # next_client_id = 0
    CLIENT_ID_LEN = 8  # in bytes

    def __init__(self, port: int):
        """ Constructor. """
        super(AuthServer, self).__init__()
        load_dotenv()
        self.google_client_id = os.environ['GOOGLE_CLIENT_ID']
        self.google_client_secret = os.environ['GOOGLE_CLIENT_SECRET']

        self.port = port
        self.app = Flask(__name__)
        self.app.add_url_rule('/auth/google', 'google_auth',
                              self.google_auth, methods=['POST'])
        self.app.add_url_rule('/auth/name', 'name_auth',
                              self.name_auth, methods=['POST'])

    def run(self):
        """ Runs the server. """
        # flask reloader expects to run in the main thread,
        # and it's not the main thread, thus I must disable it.
        self.app.run(debug=True, use_reloader=False, port=self.port)

    def google_auth(self) -> dict:
        """
         Receives authorization code,
         exchanges it for refresh and access tokens,
         calls google api to get the user info,
         and sends it the client.
         """
        try:
            content = request.get_json()
            redirect_uri = content.get('redirect_uri')
            auth_code = content.get('auth_code')

            if redirect_uri and auth_code:
                access_token = self.get_access_token(redirect_uri, auth_code)
                if access_token:
                    user_info = self.get_user_info(access_token)
                    client_info = {
                        'id': self.generate_client_id().hex(),
                        'name': user_info['name'],
                        # google returns the img url in the picture attribute
                        'img_url': user_info['picture']
                    }
                    print(client_info)
                    return client_info
            return {}
        except Exception as e:
            print('AuthServer.google_auth:', e)
            return {}

    def name_auth(self) -> dict:
        """
        Receives the user name and returns it an id
        (thus authenticates it using its name only).
        """
        content = request.get_json()
        name = content.get('name')
        if name:
            client_info = {
                'id': self.generate_client_id().hex(),
                'name': name,
                'img_url': ''
            }
            return client_info
        return {}

    def get_access_token(self, redirect_uri: str, auth_code: str) -> str:
        """
        Receives the user authentication code and exchange it for
        an access token using google api.
        :param redirect_uri: the local redirect uri the user
        used to get the auth code, it must match the uri in future requests
        to google api.
        :param auth_code: the code that the user got from google api
        :returns: the user access token.
        """
        payload = {
            'code': auth_code,
            'client_id': self.google_client_id,
            'client_secret': self.google_client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        r = requests.post(AuthServer.GOOGLE_TOKEN_ENDPOINT, data=payload)
        return r.json().get('access_token', None)

    @staticmethod
    def generate_client_id() -> bytes:
        """ Generates the client id using random bytes. """
        # AuthServer.next_client_id += 1
        # return str(AuthServer.next_client_id)
        return os.urandom(AuthServer.CLIENT_ID_LEN)

    @staticmethod
    def get_user_info(access_token: str) -> dict:
        """
        Receives the user access token and
        returns the its info from google api.
        """
        url = AuthServer.GOOGLE_USER_INFO_ENDPOINT.format(access_token)
        r = requests.get(url)
        print(url, r.json())
        return r.json()
