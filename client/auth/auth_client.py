"""
    Hadar Shahar
    AuthClient.
"""
import requests
import os
import hashlib
import webbrowser
from PyQt5.QtCore import QThread, pyqtSignal
from custom_messages.client_info import ClientInfo
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

    # this signal is emitted when the client_info is received
    # from the server (after the client signs in with google)
    recv_client_info_signal = pyqtSignal(ClientInfo)

    def __init__(self, ip: str, port: int):
        """ Constructor. """
        super(AuthClient, self).__init__()
        self.server_url = f'http://{ip}:{port}'

        self.local_web_server = LocalWebServer(self.handle_auth_code)
        self.state_token = b''

    def run(self):
        self.local_web_server.run()

    def handle_auth_code(self, auth_code: str, state_token: str):
        """
        Verifies the state_token and handles the auth code:
        sends it to the server, which then returns the client info -
        a json object that contains the client id, name and img_url.
        :returns a ClientInfo object if the authentication was successful,
                 None otherwise.
        """
        if self.state_token != state_token:
            return None

        payload = {
            'redirect_uri': self.local_web_server.auth_url,
            'auth_code': auth_code
        }
        return self.send_auth_request('/auth/google', payload)

    def name_sign_in(self, name: str):
        """
        Authenticates the user using its name.
        :returns a ClientInfo object if the authentication was successful,
                 None otherwise.
        """
        return self.send_auth_request('/auth/name', {'name': name})

    def send_auth_request(self, endpoint: str, payload: dict):
        response = requests.post(self.server_url + endpoint,
                                 json=payload).json()
        if response:
            client_info = ClientInfo.from_json(response)
            self.recv_client_info_signal.emit(client_info)
            return client_info
        return None

    def google_sign_in(self):
        """ Opens the auth url in the browser. """
        # https://developers.google.com/identity/protocols/oauth2/openid-connect#createxsrftoken
        # create a state token to prevent request forgery
        self.state_token = hashlib.sha256(
            os.urandom(1024)).hexdigest()  # TODO constant

        auth_url = f"""
            {AuthClient.GOOGLE_AUTH_ENDPOINT}?
            scope=email%20profile&
            response_type=code&
            state={self.state_token}&
            redirect_uri={self.local_web_server.auth_url}&
            client_id={AuthClient.GOOGLE_CLIENT_ID}
            """.replace('\n', '').replace(' ', '')
        webbrowser.open(auth_url)
