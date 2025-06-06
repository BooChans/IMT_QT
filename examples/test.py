import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox, QLabel
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import InfiniteLine

class SineWaveCursorDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sine Wave with Cursor Toggle")

        self.x = np.linspace(0, 10, 500)
        self.y = np.sin(self.x)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        self.toggle_cb = QCheckBox("Show Cursors")
        layout.addWidget(self.toggle_cb)

        self.label1 = QLabel("Cursor 1: X=---, Y=---")
        self.label2 = QLabel("Cursor 2: X=---, Y=---")
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)

        self.plot = self.plot_widget.plot(self.x, self.y, pen='y')

        pen_dotted = pg.mkPen('m', width=2, style=Qt.DashLine)
        y_min, y_max = self.plot_widget.getViewBox().viewRange()[1]

        # Initialize cursors vertical spanning y range
        self.cursor1 = InfiniteLine(pos=2, angle=90, pen=pen_dotted, movable=True)
        self.cursor2 = InfiniteLine(pos=7, angle=90, pen=pen_dotted, movable=True)
        self.plot_widget.addItem(self.cursor1)
        self.plot_widget.addItem(self.cursor2)
        self.cursor1.hide()
        self.cursor2.hide()

        self.toggle_cb.stateChanged.connect(self.toggle_cursors)
        #self.cursor1.sigRegionChanged.connect(self.update_labels)
        #self.cursor2.sigRegionChanged.connect(self.update_labels)

        # Initial update
        #self.update_labels()

    def toggle_cursors(self, state):
        visible = state == Qt.Checked
        self.cursor1.setVisible(visible)
        self.cursor2.setVisible(visible)
        self.label1.setVisible(visible)
        self.label2.setVisible(visible)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SineWaveCursorDemo()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec_())
