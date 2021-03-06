"""
    Hadar Shahar
    BasicVideoClient.
"""
import numpy as np
from PyQt5.QtCore import pyqtSignal
from abc import abstractmethod
from client.basic_udp_client import BasicUdpClient
from client.video.udp_packet import UdpPacket
from client.video.udp_packets_handler import UdpPacketsHandler
from client.video.video_encoder import VideoEncoder


class BasicUdpVideoClient(BasicUdpClient):
    """ Definition of the abstract class BasicVideoClient. """

    # this signal indicates that a new frame was captured
    frame_captured = pyqtSignal(np.ndarray)  # cv2 image

    # this signal indicates that a new frame was received
    frame_received = pyqtSignal(np.ndarray, bytes)  # (cv2 image, client id)

    def __init__(self, ip: str, in_socket_port: int, out_socket_port: int,
                 client_id: bytes, is_sharing=True):
        """ Constructor. """
        super(BasicUdpVideoClient, self).__init__(
            ip, in_socket_port, out_socket_port, client_id, is_sharing)
        self.frame_index = 0  # for the UdpPacketsHandler

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
            data = VideoEncoder.encode_frame(frame)

            packets = UdpPacketsHandler.create_packets(self.frame_index, data)
            for p in packets:
                self.send_data(p.encode())
            self.frame_index += 1

    def receive_data_loop(self):
        """
        Receives each frame from the server,
        decodes it and shows it.
        """
        # {client id: handler that handles that packets coming from the client}
        clients_handlers: [bytes, UdpPacketsHandler] = {}

        while self.running:
            sender_id, data = self.receive_data()
            if data is None:
                continue

            if sender_id not in clients_handlers:
                clients_handlers[sender_id] = UdpPacketsHandler()

            p = UdpPacket.decode(data)
            if p is None:  # invalid packet
                continue

            buffer = clients_handlers[sender_id].process_packet(p)
            if buffer is not None:
                frame = VideoEncoder.decode_frame_buffer(buffer)
                self.frame_received.emit(frame, sender_id)
