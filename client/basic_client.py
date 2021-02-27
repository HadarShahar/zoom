"""
    Hadar Shahar
    The basic client code.
"""
import threading
from abc import ABCMeta, abstractmethod
from PyQt5.QtCore import QThread


class QABCMeta(ABCMeta, type(QThread)):
    """
    This is a metaclass used to solve the metaclass conflict
    in the class BasicClient.
    ("metaclass conflict: the metaclass of a derived class must be
    a (non-strict) subclass of the metaclasses of all its bases")

    https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict

    This conflict occurs because BasicClient must inherit from
    QtCore.QObject (or its subclasses) in order to use signals,
    and it also should be an abstract class.
    """
    pass


class BasicClient(QThread, metaclass=QABCMeta):
    """
    Definition of the abstract class BasicClient.

    This class must inherit from QtCore.QThread and not threading.Thread
    because new signals are defined in its sub-classes.
    New signals should only be defined in sub-classes of QObject.

    It's also an abstract class (it's metaclass is derived from ABCMeta)
    because it contains abstract methods.
    """

    def __init__(self, client_id: bytes, is_sharing=True):
        """ Constructor. """
        super(BasicClient, self).__init__()
        self.id = client_id
        self.is_sharing = is_sharing
        self.running = True

    def toggle_is_sharing(self):
        """
        Toggles the is_sharing property and
        starts a thread that sends data if it starts sharing data.
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
        # TODO check loading issue
        threading.Thread(target=self.catch_exception,
                         args=(self.send_data_loop,)).start()
        # t = QThread()
        # t.run = self.start_send_data_loop
        # t.start()
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

    @abstractmethod
    def send_data_loop(self):
        """
        Sends data to the server in a loop
        the clients implement this method.
        """
        pass

    @abstractmethod
    def receive_data_loop(self):
        """
        Receives data from the server in a loop
        the clients implement this method.
        """
        pass

    def close(self):
        """ Stops running. """
        print('closing')
        self.running = False
