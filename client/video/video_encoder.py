"""
    Hadar Shahar
    VideoEncoder.
"""
import cv2
import numpy as np


class VideoEncoder(object):
    """ Definition of the class VideoEncoder. """

    # the quality of the image from 0 to 100 (the higher is the better)
    JPEG_QUALITY = 80  # default is 95

    @staticmethod
    def encode_frame(frame: np.ndarray) -> bytes:
        """
        Receives a frame, encodes it to JPEG format
        and converts it to bytes.
        """
        # change the quality of the image
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),
                        VideoEncoder.JPEG_QUALITY]
        flag, encoded_image = cv2.imencode('.jpg', frame, encode_param)
        data = encoded_image.tobytes()
        return data

    @staticmethod
    def decode_frame_buffer(buffer: bytes) -> np.ndarray:
        """ Decodes the buffer as a cv2 image. """
        # unit8 = the dtype of the encoded_image
        frame = np.frombuffer(buffer, dtype=np.uint8)
        return cv2.imdecode(frame, cv2.IMREAD_COLOR)
