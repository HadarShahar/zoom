"""
    Hadar Shahar
    AuthServer.
"""
import socket
import os
import threading
import requests
import json
from dotenv import load_dotenv
from constants import NUMBER_OF_WAITING_CONNECTIONS
from tcp_network_protocol import send_packet, recv_packet


class AuthServer(threading.Thread):
    """ Definition of the class AuthServer. """

    GOOGLE_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
    GOOGLE_USER_INFO_ENDPOINT = \
        'https://www.googleapis.com/oauth2/v3/userinfo?access_token={}'

    def __init__(self, ip: str, port: int):
        """ Constructor. """
        super(AuthServer, self).__init__()
        load_dotenv()
        self.google_client_id = os.environ['GOOGLE_CLIENT_ID']
        self.google_client_secret = os.environ['GOOGLE_CLIENT_SECRET']

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))

        self.socket.listen(NUMBER_OF_WAITING_CONNECTIONS)

    def run(self):
        """ Runs the server. """
        try:
            while True:
                client_socket, address = self.socket.accept()
                threading.Thread(target=self.handle_single_client,
                                 args=(client_socket,)).start()
        except socket.error as e:
            print('AuthServer.run:', e)

    def handle_single_client(self, client_socket: socket.socket):
        """
         Handles singe client:
         receives its authorization code,
         exchanges it for refresh and access tokens,
         calls google api to get the user info,
         and sends it the client.
         """
        try:
            redirect_uri = recv_packet(client_socket)
            done = False
            while not done:
                auth_code = recv_packet(client_socket)
                access_token = self.get_access_token(redirect_uri.decode(),
                                                     auth_code.decode())
                if access_token:
                    user_info = self.get_user_info(access_token)
                    send_packet(client_socket, json.dumps(user_info).encode())
                    done = True
                else:
                    # TODO
                    pass
        except socket.error as e:
            print('AuthServer.handle_single_client:', e)
        finally:
            client_socket.close()

    def get_access_token(self, redirect_uri: str, auth_code: str) -> str:
        payload = {
            'code': auth_code,
            'client_id': self.google_client_id,
            'client_secret': self.google_client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        r = requests.post(AuthServer.GOOGLE_TOKEN_ENDPOINT, data=payload)
        print(r.json())
        return r.json().get('access_token', None)

    @staticmethod
    def get_user_info(access_token: str) -> dict:
        url = AuthServer.GOOGLE_USER_INFO_ENDPOINT.format(access_token)
        r = requests.get(url)
        print(url, r.json())
        return r.json()
