"""
    Hadar Shahar
    The slider code.
"""
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal


class Slider(QtWidgets.QFrame):
    """ Definition of the class Slider. """

    # this signal is emitted when the slider value is changed
    value_changed = pyqtSignal(int)

    def __init__(self, parent: QtWidgets.QWidget, text: str,
                 min_val: int, max_val: int, val=None, tick_interval=1):
        """ Constructor. """
        super(Slider, self).__init__(parent)
        self.text = text
        if val is None:
            val = (min_val + max_val) // 2

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.update_label(val)
        self.layout.addWidget(self.label)

        self.sl = QtWidgets.QSlider(Qt.Horizontal, self)
        self.sl.setRange(min_val, max_val)
        self.sl.setValue(val)
        self.sl.setTickInterval(tick_interval)
        self.sl.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sl.valueChanged.connect(self.update_label)
        self.layout.addWidget(self.sl)

    def update_label(self, value: int):
        """ Updates the label's text. """
        self.label.setText(f'{self.text}: {value}')
        self.value_changed.emit(value)
