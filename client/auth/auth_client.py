"""
    Hadar Shahar
    AuthClient.
"""
from typing import Union
import requests
import json
from http import HTTPStatus
import os
import hashlib
import webbrowser
from PyQt5.QtCore import QThread, pyqtSignal
from network.custom_messages.client_info import ClientInfo
from client.network_constants import Constants
from client.auth.local_web_server import LocalWebServer


class AuthClient(QThread):
    """
    Definition of the class AuthClient.
    This class must inherit from QtCore.QThread and not threading.Thread
    because a signal is defined in it.
    New signals should only be defined in sub-classes of QObject.
    """

    GOOGLE_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
    GOOGLE_CLIENT_ID = '382513461169-7040mfbqacu9kivjm6ktibc1t3i5q67l' \
                       '.apps.googleusercontent.com'
    # the number of random bytes the state token will be generated from
    STATE_TOKEN_SEED_LEN = 1024

    # timeout for the logout request, so the request won't slow down the exit
    # small number because it doesn't need the response
    LOGOUT_REQUEST_TIMEOUT = 0.1  
    
    # this signal is emitted when the client_info is received
    # from the server (after the client signs in)
    recv_client_info_signal = pyqtSignal(ClientInfo)

    network_error = pyqtSignal(str)  # details
    invalid_id_error = pyqtSignal(str)  # details

    def __init__(self):
        """ Constructor. """
        super(AuthClient, self).__init__()
        self.server_url = \
            f'http://{Constants.SERVER_IP}:{Constants.AUTH_SERVER_PORT}'

        self.local_web_server = LocalWebServer(self.handle_auth_code)
        self.state_token = b''
        self.client_info = None

    def run(self):
        """
        Starts the local web server that receives
        the client's auth code from google.
        """
        self.local_web_server.run()

    def handle_auth_code(self, auth_code: str, state_token: str) -> \
            Union[ClientInfo, None]:
        """
        Verifies the state_token and handles the auth code:
        sends it to the server, which then returns the client info -
        a json object that contains the client id, name and img_url.
        :returns: a ClientInfo object if the authentication was successful,
                  None otherwise.
        """
        if self.state_token != state_token:
            return None

        payload = {
            'redirect_uri': self.local_web_server.auth_url,
            'auth_code': auth_code
        }
        return self.send_auth_request('/auth/google', payload)

    def name_sign_in(self, name: str) -> Union[ClientInfo, None]:
        """
        Authenticates the user using its name.
        :returns: a ClientInfo object if the authentication was successful,
                  None otherwise.
        """
        return self.send_auth_request('/auth/name', {'name': name})

    def google_sign_in(self):
        """ Opens the auth url in the browser. """
        self.generate_state_token()
        auth_url = f"""
            {AuthClient.GOOGLE_AUTH_ENDPOINT}?
            scope=email%20profile&
            response_type=code&
            state={self.state_token}&
            redirect_uri={self.local_web_server.auth_url}&
            client_id={AuthClient.GOOGLE_CLIENT_ID}
            """.replace('\n', '').replace(' ', '')
        webbrowser.open(auth_url)

    def new_meeting(self) -> Union[ClientInfo, None]:
        """
        Sends a request to create a new meeting and returns the response.
        """
        payload = {'id': self.client_info.id.hex()}
        return self.send_auth_request('/new-meeting', payload)

    def join_meeting(self, hex_meeting_id: str) -> Union[ClientInfo, None]:
        """
        Sends a request to join to a meeting with a given id
        and returns the response.
        """
        payload = {'id': self.client_info.id.hex(),
                   'meeting_id': hex_meeting_id}
        return self.send_auth_request('/join-meeting', payload)

    def logout(self):
        """
        Sends a request to log the user out
        if it's logged in.
        """
        if self.client_info is None:
            # the user is not logged in
            return
        payload = {'id': self.client_info.id.hex()}
        print('logout:', payload)
        try:
            requests.post(self.server_url + '/logout', json=payload,
                          timeout=AuthClient.LOGOUT_REQUEST_TIMEOUT)  
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout):
            pass

    def send_auth_request(self, endpoint: str, payload: dict) -> \
            Union[ClientInfo, None]:
        """
        Sends an auth request to the given endpoint in the server
        with the given payload,
         and emits a signal with some data according to the response.
        :returns: a ClientInfo object if the authentication was successful,
                  None otherwise.
        """
        try:
            response = requests.post(self.server_url + endpoint, json=payload)
            if response.ok:
                client_info = ClientInfo.from_json(response.json())
                self.client_info = client_info
                self.recv_client_info_signal.emit(client_info)
                return client_info
            elif response.status_code == HTTPStatus.NOT_FOUND:
                self.invalid_id_error.emit(f'{response.json().get("message")}')
            else:
                self.network_error.emit(f'[{response.reason}]\n' +
                                        f'{response.json().get("message")}')
        except requests.exceptions.ConnectionError:
            self.network_error.emit('The server is down, '
                                    'please try again later.')
        except json.decoder.JSONDecodeError:
            self.network_error.emit('Invalid json response.')

    def generate_state_token(self):
        """
        Creates a state token to prevent request forgery.
        https://developers.google.com/identity/protocols/oauth2/openid-connect#createxsrftoken
        """
        random_bytes = os.urandom(AuthClient.STATE_TOKEN_SEED_LEN)
        self.state_token = hashlib.sha256(random_bytes).hexdigest()
