"""
    Hadar Shahar
    The video camera code.
"""
import cv2
import threading


class VideoCamera(object):
    """ Definition of the class VideoCamera. """

    # the VideoCapture image size
    DEFAULT_VIDEO_WIDTH = 640
    DEFAULT_VIDEO_HEIGHT = 480
    DIVIDER = 1
    VIDEO_WIDTH = DEFAULT_VIDEO_WIDTH / DIVIDER
    VIDEO_HEIGHT = DEFAULT_VIDEO_HEIGHT / DIVIDER

    # the quality of the image from 0 to 100 (the higher is the better)
    JPEG_QUALITY = 80  # default is 95

    # 1 to flip the image around the y-axis (0 to flip around the x-axis)
    FLIP_AXIS = 1

    def __init__(self):
        """ Constructor. """
        self.cap = None

        # try to connect to the camera in a separate thread
        # because it might take some time
        thread = threading.Thread(target=self.connect_to_camera)
        thread.daemon = True  # so it won't prevent the app from exiting
        thread.start()

        # self.connect_to_camera()
        # if not self.cap.isOpened():
        #     print('No camera detected')

    def connect_to_camera(self):
        """
        Initializes the VideoCapture object
        and sets the frame size.
        """
        print('trying to connect to camera')
        # capture from device 0
        self.cap = cv2.VideoCapture(0)

        if self.cap.isOpened():
            print('Connected to camera')

            # change the VideoCapture frame size
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, VideoCamera.VIDEO_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VideoCamera.VIDEO_HEIGHT)

    def get_frame(self, show=False):
        """
        Reads a frame from the camera.
        Returns a numpy array (np.ndarray) if the frame was read successfully,
        otherwise None.
        """
        if self.cap is None:
            return None

        if self.cap.isOpened():
            retval, frame = self.cap.read()
            # if a frame was read successfully
            if retval:
                frame = cv2.flip(frame, VideoCamera.FLIP_AXIS)
                if show:
                    cv2.imshow('my frame', frame)
                    cv2.waitKey(1)
                return frame
            else:
                print('The frame was not read correctly, '
                      'maybe the camera is already in use.')
        self.connect_to_camera()

    def __del__(self):
        """
        This method is a destructor method,
        which is called as soon as all references
        of the object are deleted - when it's garbage collected.
        It releases the capture and destroys all cv2 open windows.
        """
        self.cap.release()
        cv2.destroyAllWindows()


def main():
    """ Tests the VideoCamera. """
    camera = VideoCamera()
    while True:
        camera.get_frame(show=True)


if __name__ == '__main__':
    main()
