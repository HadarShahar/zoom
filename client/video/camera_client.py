"""
    Hadar Shahar
    The camera client code.
"""
from client.video.basic_udp_video_client import BasicUdpVideoClient
from client.video.video_camera import VideoCamera


class CameraClient(BasicUdpVideoClient):
    """ Definition of the class CameraClient. """

    def __init__(self, ip: str, in_socket_port: int,
                 out_socket_port: int, client_id: bytes):
        """ Constructor. """
        super(CameraClient, self).__init__(
            ip, in_socket_port, out_socket_port, client_id)
        self.camera = VideoCamera()

    def get_frame(self):
        """
        Returns a frame from the camera or
        None (if it wasn't read successfully).
        """
        return self.camera.get_frame()
