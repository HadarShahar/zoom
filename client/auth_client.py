"""
    Hadar Shahar
    AuthClient.
"""
import socket
import threading
import os
import hashlib
import json
import webbrowser
from flask import Flask, request
from tcp_network_protocol import send_packet, recv_packet


class LocalWebServer(threading.Thread):
    """
    Definition of the class LocalWebServer.
    It's only used to get the auth code from google.
    https://developers.google.com/identity/protocols/oauth2/native-app#loopback-ip-address
    """

    def __init__(self, auth_code_handler, port=5000):
        """ Constructor. """
        super(LocalWebServer, self).__init__()
        self.auth_code_handler = auth_code_handler
        self.port = port

        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'index', self.index)

    def run(self):
        """ Runs the server. """
        # flask reloader expects to run in the main thread,
        # and it's not the main thread, thus I must disable it.
        self.app.run(debug=True, use_reloader=False, port=self.port)  # TODO debug=False

    def index(self):
        print(request.values)
        auth_code = request.values.get('code', None)
        if auth_code:
            state_token = request.values.get('state', None)
            user_info = self.auth_code_handler(auth_code, state_token)
            if user_info:
                return f'Hello {user_info["name"]}!'
            return 'Malformed authorization response.'
        return ''

    def shutdown(self):
        """
        Shutdown the server.
        The shutdown functionality is written in a way that the server will
        finish handling the current request and then stop.
        http://web.archive.org/web/20190706125149/http://flask.pocoo.org/snippets/67
        """
        print('closing server')
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()


class AuthClient(threading.Thread):
    """ Definition of the class AuthClient. """

    GOOGLE_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
    GOOGLE_CLIENT_ID = '382513461169-7040mfbqacu9kivjm6ktibc1t3i5q67l' \
                       '.apps.googleusercontent.com'

    def __init__(self, ip: str, port: int, user_info_callback):
        """ Constructor. """
        super(AuthClient, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.user_info_callback = user_info_callback

        self.local_web_server = LocalWebServer(self.handle_auth_code)
        self.redirect_uri = f'http://127.0.0.1:{self.local_web_server.port}'
        # send the local redirect uri to the server
        send_packet(self.socket, self.redirect_uri.encode())

        self.state_token = b''

    def run(self):
        self.local_web_server.start()

    def handle_auth_code(self, auth_code: str, state_token: str) -> dict:
        """
        Verifies the state_token and handles the auth code:
        sends it to the server, which then returns the user info -
        a json object that contains the username, email, picture url and more.
        """
        if self.state_token != state_token:
            return {}

        send_packet(self.socket, auth_code.encode())
        raw_user_info = recv_packet(self.socket)
        user_info = json.loads(raw_user_info.decode())
        self.user_info_callback(user_info)
        return user_info

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
            redirect_uri={self.redirect_uri}&
            client_id={AuthClient.GOOGLE_CLIENT_ID}
            """.replace('\n', '').replace(' ', '')
        webbrowser.open(auth_url)

    def close(self):
        """ Closes the socket and the local server. """
        self.socket.close()
        self.local_web_server.shutdown()
