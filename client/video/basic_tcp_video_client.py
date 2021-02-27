"""
    Hadar Shahar
    BasicTcpVideoClient.
"""
import numpy as np
import cv2
from PyQt5.QtCore import pyqtSignal
from abc import abstractmethod
from constants import CHUNK_SIZE, EOF, JPEG_QUALITY
from tcp_network_protocol import recv_packet
from client.basic_tcp_client import BasicTcpClient


class BasicTcpVideoClient(BasicTcpClient):
    """ Definition of the abstract class BasicTcpVideoClient. """

    # this signal indicates that a new frame was captured
    frame_captured = pyqtSignal(np.ndarray)  # cv2 image

    # this signal indicates that a new frame was received
    frame_received = pyqtSignal(np.ndarray, bytes)  # (cv2 image, client id)

    def __init__(self, ip: str, in_socket_port: int, out_socket_port: int,
                 client_id: bytes, is_sharing=True):
        """ Constructor. """
        super(BasicTcpVideoClient, self).__init__(
            ip, in_socket_port, out_socket_port, client_id, is_sharing)

    @abstractmethod
    def get_frame(self):
        """
        Returns a frame, or None if it wasn't read successfully.
        The CameraClient and ShareScreenClient implement this method.
        """
        pass

    def send_data_loop(self):
        """
        Captures video from the camera and
        sends each frame to the server.
        """
        while self.running and self.is_sharing:
            frame = self.get_frame()

            # if the frame was not read successfully
            # can't check 'if not frame:' because an exception is raised
            if frame is None:
                continue

            # send a signal to show the frame in the gui
            self.frame_captured.emit(frame)

            # convert the frame (numpy.ndarray) to bytes
            data = BasicTcpVideoClient.encode_frame(frame)
            # send the data in chunks to the server
            for i in range(0, len(data), CHUNK_SIZE):
                chunk = data[i: i + CHUNK_SIZE]
                self.send_packet(chunk)
            self.send_packet(EOF)

    def receive_data_loop(self):
        """
        Receives each frame from the server,
        decodes it and shows it.
        """
        clients_buffers: [bytes, bytearray] = {}
        # {client id: buffer of data received from the client}

        while self.running:
            # bytearray is unhashable => can't be a dictionary key
            sender_id = bytes(recv_packet(self.in_socket))
            # receive the frame in chunks
            data = recv_packet(self.in_socket)
            if data != EOF:
                if sender_id in clients_buffers:
                    clients_buffers[sender_id].extend(data)
                else:
                    clients_buffers[sender_id] = bytearray(data)
            else:
                frame = self.decode_frame_buffer(clients_buffers[sender_id])

                if frame is not None:  # TODO check why frame can be None
                    # cv2.imshow(f'frame from client {sender_id}', frame)
                    # cv2.waitKey(1)
                    self.frame_received.emit(frame, sender_id)
                else:
                    print('check why this happened ', '#'*30, sender_id, frame)

                clients_buffers[sender_id] = bytearray()

    @staticmethod
    def encode_frame(frame: np.ndarray) -> bytes:
        """
        Receives a frame, encodes it to JPEG format
        and converts it to bytes.
        """
        # change the quality of the image
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        flag, encoded_image = cv2.imencode('.jpg', frame, encode_param)
        data = encoded_image.tobytes()
        return data

    @staticmethod
    def decode_frame_buffer(buffer: bytes):
        """ Decodes the buffer as a cv2 image. """
        # unit8 = the dtype of the encoded_image
        frame = np.frombuffer(buffer, dtype=np.uint8)
        return cv2.imdecode(frame, cv2.IMREAD_COLOR)
