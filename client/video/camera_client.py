"""
    Hadar Shahar
    The camera client code.
"""
from client.network_constants import Constants
from client.video.basic_udp_video_client import BasicUdpVideoClient
from client.video.video_camera import VideoCamera


class CameraClient(BasicUdpVideoClient):
    """ Definition of the class CameraClient. """

    def __init__(self, client_id: bytes):
        """ Constructor. """
        super(CameraClient, self).__init__(
            Constants.SERVER_IP, Constants.CLIENT_IN_VIDEO_PORT,
            Constants.CLIENT_OUT_VIDEO_PORT, client_id)
        self.camera = VideoCamera()

    def get_frame(self):
        """
        Returns a frame from the camera or
        None (if it wasn't read successfully).
        """
        return self.camera.get_frame()

    def close(self):
        """ Closes th camera. """
        super(CameraClient, self).close()
        self.camera.close()
