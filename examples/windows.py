import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import LineSegmentROI
from scipy.ndimage import map_coordinates

print("TOP-LEVEL: importing", __name__)



class RealTimeCrossSectionViewer(QMainWindow):
    """
    A PyQt5-based GUI for interactively exploring 2D slices from a 3D volume 
    and extracting line profile cross-sections in real time.
    """
    def __init__(self, volume_data):
        super().__init__()
        self.volume = volume_data
        self.current_slice = 0
        self.setup_ui()
        self.setup_interaction()

    def setup_ui(self):
        self.setWindowTitle("FFT Cross-Section Viewer")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.splitter = QSplitter(Qt.Vertical, self.central_widget)
        self.splitter.setSizes([700, 300])

        self.layout = QVBoxLayout(self.central_widget)
        
        self.slice_view = pg.ImageView()

        self.layout.addWidget(QLabel("Zoom:"))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setValue(0)
        self.layout.addWidget(self.slider)

        self.slice_view.setImage(self.volume[self.current_slice])
        self.splitter.addWidget(self.slice_view)
        view = self.slice_view.getView()
        view.setRange(xRange=(0, self.volume.shape[2]), yRange=(0, self.volume.shape[1]), padding=0)

        h, w = self.volume.shape[1], self.volume.shape[2]
        center_x, center_y = w // 2, h // 2
        offset = 25

        self.line = LineSegmentROI(
            positions=[[center_x - offset, center_y], [center_x + offset, center_y]],
            pen=pg.mkPen('r', width=3),
            movable=True,
            rotatable=True,
            resizable=True
        )
        self.slice_view.getView().addItem(self.line)

        self.cross_section_container = QWidget()
        cross_layout = QVBoxLayout(self.cross_section_container)
        self.cross_section_plot = pg.PlotWidget()
        cross_layout.addWidget(self.cross_section_plot)

        self.splitter.addWidget(self.cross_section_container)
        self.layout.addWidget(self.splitter)

        self.toggle_line_cb = QCheckBox("Show Line ROI & Cross-section")
        self.layout.addWidget(self.toggle_line_cb)
        self.toggle_line_cb.setChecked(True)
        self.toggle_line_cb.stateChanged.connect(self.toggle_line_roi)

        self.vline = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g'))
        self.hline = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('g'))
        self.cross_section_plot.addItem(self.vline, ignoreBounds=True)
        self.cross_section_plot.addItem(self.hline, ignoreBounds=True)

        self.cursor_label = QLabel("X: ---, Y: ---")
        cross_layout.addWidget(self.cursor_label)


    def setup_interaction(self):
        self.line.sigRegionChanged.connect(self.update_cross_section)
        self.slider.valueChanged.connect(self.update_zoom)
        self.cross_section_plot.scene().sigMouseMoved.connect(self.mouse_moved_on_plot)
        self.update_zoom(self.slider.value())
        self.update_cross_section()

    def toggle_line_roi(self, state):
        if state == Qt.Checked:
            self.line.show()
            self.cross_section_container.show()
            self.update_cross_section()
        else:
            self.line.hide()
            self.cross_section_container.hide()

    def update_cross_section(self):
        try:
            state = self.line.getState()
            start = state['points'][0] + state['pos']
            end = state['points'][1] + state['pos']
            n_samples = 300
            x = np.linspace(start[0], end[0], n_samples)
            y = np.linspace(start[1], end[1], n_samples)

            valid_mask = (x >= 0) & (x <= self.volume.shape[2] - 1) & \
                         (y >= 0) & (y <= self.volume.shape[1] - 1)

            x_safe = np.copy(x)
            y_safe = np.copy(y)
            x_safe[~valid_mask] = -1
            y_safe[~valid_mask] = -1

            x = np.clip(x, 0, self.volume.shape[2] - 1)
            y = np.clip(y, 0, self.volume.shape[1] - 1)

            profile = map_coordinates(
                self.volume[self.current_slice],
                np.vstack([x, y]),
                order=1,
                mode='constant',
                cval=0.0
            )

            profile[~valid_mask] = 0
            self.cross_section_plot.clear()
            self.cross_section_plot.plot(profile, pen='y')

        except Exception as e:
            print(f"Update error: {str(e)}")

    def update_zoom(self, slider_value):
        zoom_size = self.slider.maximum() - slider_value + self.slider.minimum()
        h, w = self.volume.shape[1], self.volume.shape[2]
        center_x, center_y = w // 2, h // 2
        half = zoom_size // 2
        self.slice_view.getView().setRange(
            xRange=(center_x - half, center_x + half),
            yRange=(center_y - half, center_y + half),
            padding=0
        )

    def mouse_moved_on_plot(self, pos):
        vb = self.cross_section_plot.getViewBox()
        if vb.sceneBoundingRect().contains(pos):
            mouse_point = vb.mapSceneToView(pos)
            x = mouse_point.x()
            y = mouse_point.y()
            self.vline.setPos(x)
            self.hline.setPos(y)
            self.cursor_label.setText(f"X: {x:.1f}, Y: {y:.3f}")


if __name__ == "__main__":

    print("Before QApplication")
    app = QApplication([])
    print("After QApplication")


    z_dim, y_dim, x_dim = 100, 256, 256
    x = np.arange(x_dim)
    y = np.arange(y_dim)
    xx, yy = np.meshgrid(x, y)
    chessboard_2d = ((xx // 32 + yy // 32) % 2).astype(float)
    data = np.stack([chessboard_2d for _ in range(z_dim)], axis=0)

    print("Before creating viewer")
    viewer = RealTimeCrossSectionViewer(data)
    print("After creating viewer")
    viewer.resize(1000, 800)
    viewer.show()
    app.exec_()