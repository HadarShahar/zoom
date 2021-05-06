"""
    Hadar Shahar
    AuthServer.
"""
import os
import threading
import requests
from flask import Flask, request, make_response, Response
from http import HTTPStatus
import string
from dotenv import load_dotenv
from typing import Union
from network.custom_messages.client_info import ClientInfo
from server.ids_config import MEETING_ID_LEN, CLIENT_ID_LEN


class AuthServer(threading.Thread):
    """ Definition of the class AuthServer. """

    GOOGLE_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
    GOOGLE_USER_INFO_ENDPOINT = \
        'https://www.googleapis.com/oauth2/v3/userinfo?access_token={}'

    MAX_CLIENTS_PER_MEETING = 4

    # colors for missing credentials error
    COLORS_FAIL = '\033[91m'
    COLORS_ENDC = '\033[0m'
    MISSING_OAUTH_CRED_ERROR = 'Missing server OAuth 2.0 credentials: ' \
                               'GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET.\n' \
                               'Cannot authenticate the user using google API.'

    def __init__(self, port: int):
        """ Constructor. """
        super(AuthServer, self).__init__()
        self.port = port
        self.app = Flask(__name__)

        load_dotenv()
        self.google_client_id = os.environ.get('GOOGLE_CLIENT_ID', None)
        self.google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET',
                                                   None)
        if not self.google_client_id or not self.google_client_secret:
            print(AuthServer.COLORS_FAIL +
                  AuthServer.MISSING_OAUTH_CRED_ERROR +
                  AuthServer.COLORS_ENDC)

        self.create_endpoints()

        # { client_id: ClientInfo(...) }
        self.authenticated_clients: [bytes, ClientInfo] = {}
        self.authenticated_clients_lock = threading.Lock()

        # { meeting_id: [first_client_id, second_client_id, ...] }
        self.meetings_dict: [bytes, [bytes]] = {}
        self.meetings_dict_lock = threading.Lock()

    def create_endpoints(self):
        """ Creates endpoints for the server. """
        self.app.add_url_rule('/auth/google', 'google_auth',
                              self.google_auth, methods=['POST'])
        self.app.add_url_rule('/auth/name', 'name_auth',
                              self.name_auth, methods=['POST'])

        self.app.add_url_rule('/new-meeting', 'new_meeting',
                              self.new_meeting, methods=['POST'])
        self.app.add_url_rule('/join-meeting', 'join_meeting',
                              self.join_meeting, methods=['POST'])
        self.app.add_url_rule('/logout', 'logout',
                              self.logout, methods=['POST'])

    def run(self):
        """ Runs the server. """
        # flask reloader expects to run in the main thread,
        # and it's not the main thread, thus I must disable it.
        self.app.run(debug=True, use_reloader=False,
                     host='0.0.0.0', port=self.port)

    def google_auth(self) -> Response:
        """
         Receives authorization code,
         exchanges it for refresh and access tokens,
         calls google api to get the user info,
         and sends it the client.
         """
        if not self.google_client_id or not self.google_client_secret:
            return self.error_response(AuthServer.MISSING_OAUTH_CRED_ERROR,
                                       HTTPStatus.INTERNAL_SERVER_ERROR)

        try:
            content = request.get_json()
            redirect_uri = content.get('redirect_uri')
            auth_code = content.get('auth_code')

            if not redirect_uri or not auth_code:
                return self.error_response(
                    'Missing required params: "redirect_uri", "auth_code".')

            access_token = self.get_access_token(redirect_uri, auth_code)
            if not access_token:
                return self.error_response('Invalid request.')
            user_info = self.get_user_info(access_token)

            client_id = self.generate_client_id()
            # no meeting id because the client still hasn't join a meeting
            meeting_id = b''
            # google returns the img url in the picture attribute
            img_url = user_info['picture']

            client_info = ClientInfo(client_id, meeting_id,
                                     user_info['name'], img_url)

            with self.authenticated_clients_lock:
                self.authenticated_clients[client_id] = client_info
            self.print_clients()
            return make_response(client_info.json())

        except Exception as e:
            print('AuthServer.google_auth:', e)
            return self.error_response(str(e),
                                       HTTPStatus.INTERNAL_SERVER_ERROR)

    def name_auth(self) -> Response:
        """
        Receives the user name and returns it an id
        (thus authenticates it using its name only).
        """
        content = request.get_json()
        name = content.get('name')
        if not name:
            return self.error_response('Missing required "name" param.')

        client_id = self.generate_client_id()
        # no meeting id because the client still hasn't join a meeting
        meeting_id = b''
        img_url = ''  # no image url
        client_info = ClientInfo(client_id, meeting_id, name, img_url)

        with self.authenticated_clients_lock:
            self.authenticated_clients[client_id] = client_info
        self.print_clients()
        return make_response(client_info.json())

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

    def new_meeting(self) -> Response:
        """
        Receives the client id from the request and
        tries to create a new meeting and add the client to it.
        :returns: A Response object based on the result of the operation.
        """
        hex_client_id = request.get_json().get('id')
        client_info, error_resp = self.check_joining_client(hex_client_id)
        if error_resp:
            return error_resp

        meeting_id = self.generate_meeting_id()
        with self.meetings_dict_lock:
            self.meetings_dict[meeting_id] = [client_info.id]

        client_info.meeting_id = meeting_id
        return AuthServer.joined_successfully_response(client_info)

    def join_meeting(self) -> Response:
        """
        Receives the client id and the meeting id from the request and
        tries to join the client to the meeting.
        :returns: A Response object based on the result of the operation.
        """
        content = request.get_json()
        hex_client_id = content.get('id')
        client_info, error_resp = self.check_joining_client(hex_client_id)
        if error_resp:
            return error_resp

        hex_meeting_id = content.get('meeting_id')
        if not hex_meeting_id:
            return self.error_response('Missing required "meeting_id" param.')
        if not AuthServer.is_hex_string(hex_meeting_id):
            return self.error_response('Invalid meeting ID.',
                                       HTTPStatus.NOT_FOUND)
        meeting_id = bytes.fromhex(hex_meeting_id)

        with self.meetings_dict_lock:
            if meeting_id not in self.meetings_dict:
                return self.error_response('Invalid meeting ID.',
                                           HTTPStatus.NOT_FOUND)
            if len(self.meetings_dict[meeting_id]) == \
                    AuthServer.MAX_CLIENTS_PER_MEETING:
                return self.error_response('This meeting is full.',
                                           HTTPStatus.FORBIDDEN)
            self.meetings_dict[meeting_id].append(client_info.id)

        client_info.meeting_id = meeting_id
        return AuthServer.joined_successfully_response(client_info)

    def check_joining_client(self, hex_client_id: str) -> \
            (Union[ClientInfo, None], Union[Response, None]):
        """
        Given a client id as a hex string,
        checks if the client (who is trying to join a meeting / create one)
        is authenticated and not in another meeting.
        :returns: A tuple (client_info, error_resp):
                    - client_info is the info of the authenticated client,
                      None if it's not authenticated.
                    - error_resp is an error response, None if there isn't any.
        """
        client_info = None
        error_resp = None

        if not hex_client_id:
            error_resp = self.error_response('Missing required "id" param.')
        elif not AuthServer.is_hex_string(hex_client_id):
            error_resp = self.error_response('Invalid client ID.',
                                             HTTPStatus.NOT_FOUND)
        else:
            client_id = bytes.fromhex(hex_client_id)

            # if the id contains the meeting id, remove it
            # and keep just the client id
            if len(client_id) == MEETING_ID_LEN + CLIENT_ID_LEN:
                client_id = client_id[MEETING_ID_LEN:]

            with self.authenticated_clients_lock:
                client_info = self.authenticated_clients.get(client_id)
            if not client_info:
                error_resp = self.error_response('Invalid client ID.',
                                                 HTTPStatus.NOT_FOUND)
            elif client_info.meeting_id:
                error_resp = self.error_response(
                    'The client is already in a meeting')

        return client_info, error_resp

    def logout(self) -> dict:
        """
        Logs the user out - delete its id.
        :returns: An empty response (must return something).
        """
        content = request.get_json()
        hex_client_id = content.get('id')
        if AuthServer.is_hex_string(hex_client_id):
            client_id = bytes.fromhex(hex_client_id)
            if len(client_id) == MEETING_ID_LEN + CLIENT_ID_LEN:
                client_id = client_id[MEETING_ID_LEN:]

            with self.authenticated_clients_lock:
                if client_id in self.authenticated_clients:
                    del self.authenticated_clients[client_id]
            self.print_clients()
        return {}

    def generate_meeting_id(self) -> bytes:
        """ Generates a unique meeting id using random bytes. """
        meeting_id = os.urandom(MEETING_ID_LEN)
        with self.meetings_dict_lock:
            while meeting_id in self.meetings_dict:
                meeting_id = os.urandom(MEETING_ID_LEN)
        return meeting_id

    def generate_client_id(self) -> bytes:
        """ Generates a unique client id using random bytes. """
        client_id = os.urandom(CLIENT_ID_LEN)
        with self.authenticated_clients_lock:
            while client_id in self.authenticated_clients:
                client_id = os.urandom(CLIENT_ID_LEN)
        return client_id

    def validate_client_id(self, full_client_id: bytes) -> bool:
        """
        Validates a given client id.
        :param full_client_id: the client id to be validated.
               It contains the meeting_id and the client_id.
        :returns: True if it's valid, False otherwise.
        """
        if len(full_client_id) != (MEETING_ID_LEN +
                                   CLIENT_ID_LEN):
            return False

        meeting_id = full_client_id[:MEETING_ID_LEN]
        client_id = full_client_id[MEETING_ID_LEN:]

        # "with" block always executes, even after return!
        with self.meetings_dict_lock:
            return meeting_id in self.meetings_dict and \
                   client_id in self.meetings_dict[meeting_id]

    def client_disconnected(self, full_client_id: bytes):
        """
        The main server calls this function when a client
        disconnects from a meeting.

        """
        meeting_id = full_client_id[:MEETING_ID_LEN]
        client_id = full_client_id[MEETING_ID_LEN:]

        with self.authenticated_clients_lock:
            self.authenticated_clients[client_id].meeting_id = b''

        with self.meetings_dict_lock:
            self.meetings_dict[meeting_id].remove(client_id)

            # if the meeting is now empty, delete the meeting id
            if not self.meetings_dict[meeting_id]:
                del self.meetings_dict[meeting_id]

    def print_clients(self):
        """ Prints the server clients. """
        with self.authenticated_clients_lock:
            print('authenticated clients:',
                  [client_id.hex()
                   for client_id in self.authenticated_clients.keys()])

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

    @staticmethod
    def is_hex_string(s: str) -> bool:
        """
        Returns True if a given string is a valid hex string,
        False otherwise.
        """
        hex_digits = set(string.hexdigits)
        # each byte is represented by 2 hex digits
        return len(s) % 2 == 0 and all(c in hex_digits for c in s)

    @staticmethod
    def joined_successfully_response(client_info: ClientInfo) -> \
            Response:
        """
        :param client_info: The info of the client who has successfully
                            joined the meeting.
        :returns: A Response object that contains the client info as json.
                  In this response the meeting id and client id are joined
                  to one id, so the client will treat them as one.
        """
        json = client_info.json()
        # join the ids, so the client will treat them as one
        json['id'] = (client_info.meeting_id + client_info.id).hex()
        return make_response(json)

    @staticmethod
    def error_response(msg: str, status_code=HTTPStatus.BAD_REQUEST) -> \
            Response:
        """
        Creates an error response with a given message
        and status code.
        """
        return make_response({'message': msg}, status_code)
