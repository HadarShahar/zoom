"""
    Hadar Shahar
    LocalWebServer.
"""
import socket
from flask import Flask, request


class LocalWebServer(object):
    """
    Definition of the class LocalWebServer.
    It's only used to get the auth code from google.
    https://developers.google.com/identity/protocols/oauth2/native-app#loopback-ip-address
    """

    def __init__(self, auth_code_handler):
        """ Constructor. """
        super(LocalWebServer, self).__init__()
        self.auth_code_handler = auth_code_handler
        self.port = LocalWebServer.find_free_port()

        self.app = Flask(__name__)
        self.app.add_url_rule('/auth', 'auth', self.auth)
        self.auth_url = f'http://localhost:{self.port}/auth'

    def run(self):
        """ Runs the server. """
        # flask reloader expects to run in the main thread,
        # and it's not the main thread, thus I must disable it.
        self.app.run(debug=True, use_reloader=False, port=self.port)

    def auth(self):
        """
        Authentication function which receives the auth code from google
        and forwards it to the auth_code_handler.
        """
        auth_code = request.values.get('code')
        if auth_code:
            state_token = request.values.get('state')
            client_info = self.auth_code_handler(auth_code, state_token)
            if client_info:
                self.shutdown()
                return f'Hello {client_info.name}!' \
                       f'<br>You can return to the app now.'
            return 'Network error.'
        return 'Missing required "code" param.'

    def shutdown(self):
        """
        Shutdown the server.
        The shutdown functionality is written in a way that the server will
        finish handling the current request and then stop.
        http://web.archive.org/web/20190706125149/http://flask.pocoo.org/snippets/67
        """
        print('closing local server')
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    @staticmethod
    def find_free_port() -> int:
        """ Finds a free port number. """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # when bind the socket to port 0, a random free port will be selected
        sock.bind(('localhost', 0))
        _, port = sock.getsockname()
        sock.close()
        return port
