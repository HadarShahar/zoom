"""
    Hadar Shahar
    The smart board code.
"""
import sys
import numpy as np
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QColor
from GUI.widgets.smart_board_toolbar import SmartBoardToolbar
from GUI.widgets.basic_video_widget import BasicVideoWidget
from painting import Painting


class SmartBoard(QtWidgets.QFrame):
    """ Definition of the class SmartBoard. """

    # this signal is emitted when a new painting is created
    new_painting = pyqtSignal(Painting)

    def __init__(self, parent: QtWidgets.QWidget):
        """ Initializes the different widgets of the smart board. """
        super(SmartBoard, self).__init__(parent)

        self.bg_color = '#FFFFFF'  # white
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.label = QtWidgets.QLabel(self)
        self.label.setMinimumSize(BasicVideoWidget.MIN_WIDTH,
                                  BasicVideoWidget.MIN_HEIGHT)
        # self.label.setGeometry(0, 0, self.width(), self.height())
        pixmap = QtGui.QPixmap(self.label.width(), self.label.height())
        pixmap.fill(QColor(self.bg_color))
        self.label.setPixmap(pixmap)
        self.layout.addWidget(self.label)

        self.toolbar = SmartBoardToolbar(self)
        self.layout.addWidget(self.toolbar)

        # self.pen = QtGui.QPen()
        # self.pen.setWidth(self.toolbar.pen_width)
        # self.pen.setColor(QColor(self.toolbar.pen_color))
        # self.toolbar.new_color.connect(lambda c:
        #                                self.pen.setColor(QColor(c)))
        # self.toolbar.pen_width_slider.value_changed.connect(self.pen.setWidth)
        self.toolbar.clear_button.clicked \
            .connect(lambda: self.draw_and_send(Painting(Painting.CLEAR_ALL)))

        self.last_xs = []
        self.last_ys = []

        # TODO make sliders that control these thresholds
        # the minimum line length
        self.min_line_len = 20
        # the maximum distance between each point and the line
        self.distance_threshold = 10
        # if the absolute value of the slope is less than this threshold,
        # convert it to 0
        self.slope_0_threshold = 0.05
        # if the absolute value of the difference between 2 given slopes
        # is less than this threshold, they are considered parallel
        self.parallel_slopes_threshold = 0.1

    def clear(self):
        """ Clears the board. """
        self.label.pixmap().fill(QColor(self.bg_color))
        self.update()

    def hide(self):
        """ Hides and clears the board. """
        super(SmartBoard, self).hide()
        self.clear()

    def keyPressEvent(self, e: QKeyEvent):
        """
        This function is called when a key is pressed.
        It handles the key event.
        """
        if e.key() == Qt.Key_Delete:  # clear when delete key is clicked
            self.draw_and_send(Painting(Painting.CLEAR_ALL))
        e.accept()

    def mouseMoveEvent(self, e: QMouseEvent):
        """
        This function is called on mouse move events.
        These will occur only when a mouse button is pressed down,
        unless mouse tracking has been enabled with setMouseTracking() .
        It draws and sends paintings according to the mouse event.
        """
        # if the moue is on the toolbar, ignore it
        if e.y() > (self.height() - self.toolbar.height()):
            return

        if self.last_xs:
            coordinates = (self.last_xs[-1], self.last_ys[-1], e.x(), e.y())
            painting = Painting(Painting.LINE, coordinates)
            self.draw_and_send(painting)

        self.last_xs.append(e.x())
        self.last_ys.append(e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        """
        This function is called when the mouse is released.
        It checks if the last points represent a shape.
        """
        # if it's an empty list, there are no shapes
        if not self.last_xs:
            return

        if self.check_for_line() or \
                self.check_for_rect() or \
                self.check_for_circle():
            pass

        self.last_xs = []
        self.last_ys = []

    def send_painting(self, painting: Painting):
        """ Sends a given painting. """
        self.new_painting.emit(painting)

    def draw_painting(self, painting: Painting):
        """ Shows a given painting. """
        if painting.pen_color is None:
            painting.pen_color = self.toolbar.pen_color
        if painting.pen_width is None:
            painting.pen_width = self.toolbar.pen_width

        pen = QtGui.QPen()
        pen.setColor(QColor(painting.pen_color))
        pen.setWidth(painting.pen_width)

        painter = QtGui.QPainter(self.label.pixmap())
        painter.setPen(pen)

        if painting.type == Painting.LINE:
            painter.drawLine(*painting.data)

        elif painting.type == Painting.RECTANGLE:
            painter.drawRect(*painting.data)

        elif painting.type == Painting.CLEAR_POINTS:
            points = painting.data
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                painter.drawLine(*p1, *p2)
        elif painting.type == Painting.CLEAR_ALL:
            self.clear()

        self.update()

    def draw_and_send(self, painting: Painting):
        """ Draws ans sends a given painting. """
        self.draw_painting(painting)
        self.send_painting(painting)

    def clear_points(self, xs: list, ys: list):
        """
        Clears the points - draw lines between them
        with the background color.
        """
        points = list(zip(xs, ys))
        self.draw_and_send(Painting(Painting.CLEAR_POINTS,
                                    points, self.bg_color))

    def check_for_line(self) -> bool:
        """
        Checks if the points of the last mouse moves represent a line.
        If a line was found, it draws it and sends it.
        :returns: True if a line was found, False otherwise.
        """
        xs = self.last_xs
        ys = self.last_ys

        # import matplotlib.pyplot as plt
        # try:
        #     plt.plot(xs, ys)
        #     plt.show()
        # except Exception as e:
        #     print(e)

        if self.is_slope_undefined(xs):
            # the coordinates of the new line
            start_point = (xs[0], ys[0])
            end_point = (xs[-1], ys[-1])
        else:
            f = self.get_line_function(xs, ys)
            if not f:
                return False
            # the coordinates of the new line
            start_point = (xs[0], f(xs[0]))
            end_point = (xs[-1], f(xs[-1]))

        # convert to integers
        coordinates = [int(n) for n in (*start_point, *end_point)]

        # clear the last points
        self.clear_points(xs, ys)

        painting = Painting(Painting.LINE, coordinates)
        self.draw_and_send(painting)
        return True

    def check_for_rect(self) -> bool:
        """
        """
        xs = self.last_xs
        ys = self.last_ys
        points = list(zip(xs, ys))

        top_left = self.closest_point_to_target(points, (0, 0))
        top_right = self.closest_point_to_target(points, (self.width(), 0))
        bottom_left = self.closest_point_to_target(points, (0, self.height()))
        bottom_right = \
            self.closest_point_to_target(points, (self.width(), self.height()))

        # calculate the slopes of each side
        top_slope = self.round_slope(self.slope(top_left, top_right))
        bottom_slope = self.round_slope(self.slope(bottom_left, bottom_right))
        # left_slope = self.round_slope(self.slope(top_left, bottom_left))
        # right_slope = self.round_slope(self.slope(top_right, bottom_right))

        is_rect = top_slope == bottom_slope == 0 and \
                  self.is_slope_undefined([top_left[0], bottom_left[0]]) and \
                  self.is_slope_undefined([top_right[0], bottom_right[0]])

        if not is_rect:
            return False

        # clear the last points
        self.clear_points(xs, ys)

        # paint the rectangle
        x1, y1 = top_left
        x2, y2 = bottom_right
        w = abs(x1 - x2)
        h = abs(y1 - y2)
        painting = Painting(Painting.RECTANGLE, (x1, y1, w, h))
        self.draw_and_send(painting)
        return True

    def check_for_circle(self) -> bool:
        """
        """
        xs = self.last_xs
        ys = self.last_ys
        center = (self.avg(xs), self.avg(ys))
        distances = [self.distance(center, p) for p in zip(xs, ys)]
        a, b = center
        # self.draw_painting(Painting(Painting.LINE, (a-1, b, a+1, b)))
        # print(min(distances), max(distances))
        return False

    def resizeEvent(self, e: QtGui.QResizeEvent):
        """
        This function is called when the smart board is resized.
        It scales the label's pixmap.
        """
        pixmap = self.label.pixmap().scaled(self.label.width(),
                                            self.label.height())
        self.label.setPixmap(pixmap)

    def get_line_function(self, xs: list, ys: list):
        """
        Returns the line function if it's a straight line,
        None otherwise.
        """
        # if the line length is less than the minimum length
        if SmartBoard.distance((xs[0], ys[0]),
                               (xs[-1], ys[-1])) < self.min_line_len:
            return None

        m, b = list(np.polyfit(xs, ys, 1))
        for p in zip(xs, ys):
            dist = SmartBoard.distance_point_line(p, m, b)
            if dist > self.distance_threshold:
                return None

        m = self.round_slope(m)
        if m is None:
            return None

        f = lambda x: m * x + b
        print(f'y = {m}x + {b}')
        return f

    def round_slope(self, slope: float):
        """ Rounds a given slope. """
        if slope is None:
            return None
        if abs(slope) < self.slope_0_threshold:
            return 0
        return slope

    def is_slope_undefined(self, xs: list) -> bool:
        """
        Returns True if the slope of these points is undefined -
        if the maximum distance between each x value and the average x value
        is less than the distance_threshold.
        """
        avg_x = SmartBoard.avg(xs)
        max_dist_from_avg = max([abs(x1 - avg_x) for x1 in xs])
        return max_dist_from_avg < self.distance_threshold

    def are_lines_parallel(self, slope1: float, slope2: float) -> bool:
        """ Returns True if 2 lines are parallel, False otherwise. """
        if slope1 is None:
            return slope2 is None
        if slope2 is None:
            return slope1 is None
        return abs(slope1 - slope2) < self.parallel_slopes_threshold

    # def are_lines_vertical(self, slope1: float, slope2: float) -> bool:
    #     """ Returns True if 2 lines are vertical, False otherwise. """
    #     if slope1 is None:
    #         return slope2 == 0
    #     if slope1 == 0:
    #         return slope2 is None
    #     print(abs(slope1*slope2))
    #     return False

    @staticmethod
    def distance(p1: tuple, p2: tuple) -> float:
        """ Returns the distance between 2 given points. """
        return np.sqrt((p1[0] - p2[0]) ** 2 + ((p1[1] - p2[1]) ** 2))

    @staticmethod
    def distance_point_line(point: tuple, m: float, b: float) -> float:
        """
        Returns the distance between a given point
        and a given line (represented as y=mx+b).
        """
        x, y = point
        return abs(-m * x + y - b) / np.sqrt(m ** 2 + 1)

    @staticmethod
    def closest_point_to_target(points: list, target_point: tuple) -> tuple:
        """
        Receives a list f points and a target point.
        :returns: the closest point to the target.
        """
        points_distance = {SmartBoard.distance(p, target_point): p
                           for p in points}
        min_dist = min(points_distance.keys())
        return points_distance[min_dist]
        # closest_point = points[0]
        # min_dist = SmartBoard.distance(closest_point, target_point)
        # for p in points:
        #     d = SmartBoard.distance(p, target_point)
        #     if d < min_dist:
        #         closest_point = p
        #         min_dist = d
        # return closest_point

    @staticmethod
    def slope(point1: tuple, point2: tuple):
        """
        Returns the slope between 2 given points, None if it's undefined.
        """
        x1, y1 = point1
        x2, y2 = point2
        if x2 != x1:
            return (y2 - y1) / (x2 - x1)
        return None

    @staticmethod
    def avg(nums: list) -> float:
        """ Given a list of numbers, returns the average number. """
        return sum(nums) / len(nums)


if __name__ == '__main__':
    # We don't need to create a QMainWindow since
    # any widget without a parent is a window in it's own right.
    app = QtWidgets.QApplication([])
    board = SmartBoard(None)
    board.show()
    sys.exit(app.exec_())
