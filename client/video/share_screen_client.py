"""
    Hadar Shahar
    The share screen client code.
"""
from PIL import ImageGrab
import numpy as np
import cv2
from client.video.video_client import VideoClient


class ShareScreenClient(VideoClient):
    """ Definition of the class ShareScreenClient. """

    def __init__(self, ip: str, in_socket_port: int, out_socket_port: int, client_id: bytes):
        """ Constructor. """
        super(ShareScreenClient, self).__init__(ip, in_socket_port, out_socket_port,
                                                client_id,
                                                is_sharing=False,
                                                is_camera_client=False)

    def get_frame(self) -> np.ndarray:
        """
        Takes a screenshot and converts it to an opencv image.
        :return: an opencv image.
        """
        img = ImageGrab.grab()
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
