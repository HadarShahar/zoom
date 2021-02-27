"""
    Hadar Shahar
    The share screen client code.
"""
from PIL import ImageGrab
import numpy as np
import cv2
from client.network_constants import Constants
from client.video.basic_udp_video_client import BasicUdpVideoClient


class ShareScreenClient(BasicUdpVideoClient):
    """ Definition of the class ShareScreenClient. """

    def __init__(self, client_id: bytes):
        """ Constructor. """
        super(ShareScreenClient, self).__init__(
            Constants.SERVER_IP, Constants.CLIENT_IN_SCREEN_PORT,
            Constants.CLIENT_OUT_SCREEN_PORT, client_id, is_sharing=False)

    def get_frame(self) -> np.ndarray:
        """
        Takes a screenshot and converts it to an opencv image.
        :return: an opencv image.
        """
        img = ImageGrab.grab()
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
