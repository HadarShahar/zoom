"""
    Hadar Shahar
    The basic client code.
"""
import socket
import sys
import threading
from constants import EXIT_SIGN
from network_protocol import send_packet
from PyQt5.QtCore import QThread


# TODO make it abstract class
# class BasicClient(threading.Thread):
class BasicClient(QThread):
    """
    Definition of the class BasicClient.

    This class must inherit from QtCore.QThread and not threading.Thread
    because new signals are defined in its sub-classes.
    New signals should only be defined in sub-classes of QObject.
    """

    def __init__(self, ip: str, in_socket_port: int, out_socket_port: int,
                 client_id: bytes, is_sharing=True):
        """
        Initializes input and output sockets for the BasicClient.
        """
        super(BasicClient, self).__init__()
        try:
            self.in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.in_socket.connect((ip, in_socket_port))

            self.out_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.out_socket.connect((ip, out_socket_port))

            self.id = client_id
            self.update_id()

            self.is_sharing = is_sharing
            self.running = True

        except socket.error as msg:  # TODO nice exit
            print('Connection failure: %s\n terminating program' % msg)
            sys.exit(1)

    def update_id(self):
        """
        This method sends the id to the server,
        but the InfoClient overrides this method and
        receives the id from the server.
        """
        send_packet(self.out_socket, self.id)

    def toggle_is_sharing(self):
        """
        Toggles the is_sharing property and
        starts a thread that sends data if starting sharing data.
        """
        self.is_sharing = not self.is_sharing
        if self.is_sharing:
            threading.Thread(target=self.catch_exception,
                             args=(self.send_data_loop,)).start()

    def run(self):
        """
        Runs send_data_loop in a separate thread
        and receive_data_loop in this thread.
        """
        threading.Thread(target=self.catch_exception,
                         args=(self.send_data_loop,)).start()
        self.catch_exception(self.receive_data_loop)

    def catch_exception(self, func):
        """
        Executes a function, catches any exception that is raised
        inside the function and prints it.
        """
        try:
            func()
        except Exception as e:
            # print the exception only if it occurred
            # while running and not while exiting
            if self.running:
                # __qualname__ = the path to the function: ClassName.FuncName..
                print(f'{func.__qualname__}: {e}')
                self.close()

    def send_data_loop(self):
        """
        Sends data to the server in a loop
        the VideoClient and AudioClient implement this method.
        """
        pass

    def receive_data_loop(self):
        """
        Receives data from the server in a loop
        the VideoClient and AudioClient implement this method.
        """
        pass

    def close(self):
        """
        Sends the server EXIT_SIGN (if the output socket is open)
        and closes the sockets.
        """
        print('closing')
        self.running = False

        # if self.out_socket.fileno() != -1:
        # fileno() will return -1 for closed sockets.
        if not self.out_socket._closed:
            send_packet(self.out_socket, EXIT_SIGN)
        self.in_socket.close()
        self.out_socket.close()
