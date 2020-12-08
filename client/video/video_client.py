"""
    Hadar Shahar
    The video client code.
"""
import numpy as np
import cv2
from PyQt5.QtCore import pyqtSignal
from constants import CHUNK_SIZE, EOF, JPEG_QUALITY
from network_protocol import send_packet, recv_packet
from client.basic_client import BasicClient
from client.video.video_camera import VideoCamera


class VideoClient(BasicClient):
    """ Definition of the class VideoClient. """

    # this signal indicates that a new frame was captured
    frame_captured = pyqtSignal(np.ndarray)  # cv2 image

    # this signal indicates that a new frame was received (cv2 image, client id)
    frame_received = pyqtSignal(np.ndarray, bytes)  # (cv2 image, client id)

    def __init__(self, ip: str, in_socket_port: int, out_socket_port: int,
                 client_id: bytes, is_sharing=True, is_camera_client=True):
        """ Constructor. """
        super(VideoClient, self).__init__(ip, in_socket_port, out_socket_port,
                                          client_id, is_sharing)
        # print(id(self.frame_captured))
        if is_camera_client:
            self.camera = VideoCamera()

    def get_frame(self):
        """
        :return: numpy array or None
        """
        return self.camera.get_frame()

    def send_data_loop(self):
        """
        Captures video from the camera and
        sends each frame to the server.
        """
        while self.running and self.is_sharing:
            frame = self.get_frame()

            if frame is not None:  # if a frame was read successfully
                # can't check 'if frame:' because an exception is raised

                # send a signal to show the frame in the gui
                # VideoClient.frame_captured.emit(frame)  # doesn't work
                self.frame_captured.emit(frame)

                # convert the frame (numpy.ndarray) to bytes
                data = VideoClient.frame_to_bytes(frame)
                # send the data in chunks to the server
                for i in range(0, len(data), CHUNK_SIZE):
                    chunk = data[i: i + CHUNK_SIZE]
                    send_packet(self.out_socket, chunk)
                send_packet(self.out_socket, EOF)

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
                # unit8 = the dtype of the encoded_image
                frame = np.frombuffer(clients_buffers[sender_id], dtype=np.uint8)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                if frame is not None:  # TODO check why frame can be None
                    # cv2.imshow(f'received frame from client {sender_id}', frame)
                    # cv2.waitKey(1)
                    self.frame_received.emit(frame, sender_id)

                clients_buffers[sender_id] = bytearray()

    @staticmethod
    def frame_to_bytes(frame: np.ndarray) -> bytes:
        """
        Receives a frame, encodes it to JPEG format
        and converts it to bytes.
        """
        # change the quality of the image
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        flag, encoded_image = cv2.imencode('.jpg', frame, encode_param)

        # data = pickle.dumps(encoded_image)
        data = encoded_image.tobytes()
        return data

    # def send_video(self):
    #     cap = cv2.VideoCapture(0)
    #     # change the video size (default is 640x480)
    #     cap.set(3, VIDEO_WIDTH)
    #     cap.set(4, VIDEO_HEIGHT)
    #
    #     try:
    #         while True:
    #             ret, frame = cap.read()
    #             cv2.imshow('my frame', frame)
    #             cv2.waitKey(1)
    #
    #             flag, encoded_image = cv2.imencode('.jpg', frame)
    #             data = pickle.dumps(encoded_image)
    #
    #             # use struct to make sure we have a consistent endianness on the length
    #             length = struct.pack('>Q', len(data))
    #             # sendall to make sure it blocks if there's back-pressure on the socket
    #             self.socket.sendall(length)
    #             self.socket.sendall(data)
    #
    #     except Exception as e:
    #         print(e)
    #         cap.release()
    #
    # def receive_video(self):
    #     while True:
    #
    #         raw_size = self.socket.recv(8)
    #         (length,) = struct.unpack('>Q', raw_size)
    #         data = b''
    #         while len(data) < length:
    #             # doing it in batches is generally better than trying
    #             # to do it all in one go, so I believe.
    #             to_read = length - len(data)
    #             data += self.socket.recv(
    #                 4096 if to_read > 4096 else to_read)
    #
    #         frame = pickle.loads(data)
    #         frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    #         cv2.imshow('frame', frame)
    #         print('received frame')
    #         cv2.waitKey(1)
