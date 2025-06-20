import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import LineSegmentROI, InfiniteLine
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
        self.toggle_line_cb.setChecked(False)
        self.toggle_line_cb.stateChanged.connect(self.toggle_line_roi)

        self.vline = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g'))
        self.hline = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('g'))
        self.cross_section_plot.addItem(self.vline, ignoreBounds=True)
        self.cross_section_plot.addItem(self.hline, ignoreBounds=True)
        self.vline.hide()
        self.hline.hide()

        self.cursor_label = QLabel("X: ---, Y: ---")
        cross_layout.addWidget(self.cursor_label)
        self.cursor

        self.cursor_toggle_cb = QCheckBox("Show Cursor Lines on Cross-section")
        self.layout.addWidget(self.cursor_toggle_cb)
        self.cursor_toggle_cb.stateChanged.connect(self.toggle_cursor_lines)

        pen_dotted = pg.mkPen('m', width=2, style=Qt.DashLine)

        self.cursor_line1 = InfiniteLine(pos=2, angle=90, pen=pen_dotted, movable=True)
        self.cursor_line2 = InfiniteLine(pos=7, angle=90, pen=pen_dotted, movable=True)

        self.cursor_line1.setZValue(10)  # ensure on top
        self.cursor_line2.setZValue(10)

        self.cross_section_plot.addItem(self.cursor_line1)
        self.cross_section_plot.addItem(self.cursor_line2)

        self.cursor_line1.hide()
        self.cursor_line2.hide()

        self.cursor_widget = QWidget()
        self.cursor_layout = QGridLayout(self.cursor_widget)
        self.cursor_label1 = QLabel("Line1: X=---, Y=---")
        self.cursor_label2 = QLabel("Line2: X=---, Y=---")

        self.delta_label_x = QLabel("ΔX=---")
        self.delta_label_y = QLabel("ΔY=---")

        self.cursor_layout.addWidget(self.cursor_label1, 0, 0)
        self.cursor_layout.addWidget(self.delta_label_x, 0, 1)
        self.cursor_layout.addWidget(self.cursor_label2, 1, 0)
        self.cursor_layout.addWidget(self.delta_label_y, 1, 1)

        cross_layout.addWidget(self.cursor_widget)


        # Add near your other checkboxes (e.g., after self.cursor_toggle_cb)
        self.cursor_lines_toggle_cb = QCheckBox("Enable Cursor Crosshair")
        self.layout.addWidget(self.cursor_lines_toggle_cb)
        self.cursor_lines_toggle_cb.stateChanged.connect(self.toggle_cursor_lines_visibility)

        self.prev_cursor_toggle_state = False
        self.prev_cursor_lines_toggle_state = False

        self.toggle_line_cb_original_state = False
        self.toggle_line_cb.setChecked(self.toggle_line_cb_original_state)
        self.line.setVisible(self.toggle_line_cb_original_state)
        self.cross_section_container.setVisible(self.toggle_line_cb_original_state)
        
        self.cursor_toggle_cb.setEnabled(self.toggle_line_cb_original_state)
        self.cursor_toggle_cb.setChecked(False) 
        self.cursor_widget.setVisible(False)


        self.cursor_lines_toggle_cb.setEnabled(self.toggle_line_cb_original_state) 
        self.cursor_lines_toggle_cb.setChecked(False) 
        self.cursor_label.setVisible(False)






    def setup_interaction(self):
        self.line.sigRegionChanged.connect(self.update_cross_section)
        self.slider.valueChanged.connect(self.update_zoom)
        self.cross_section_plot.scene().sigMouseMoved.connect(self.mouse_moved_on_plot)
        self.update_zoom(self.slider.value())
        self.update_cross_section()
        self.cursor_line1.sigPositionChanged.connect(self.update_cursor_labels)
        self.cursor_line2.sigPositionChanged.connect(self.update_cursor_labels)
        self.update_cursor_labels()
        self.cursor_lines_toggle_cb.toggled.connect(self.update_cursor_visibility)



    def toggle_line_roi(self, state):
        enabled = state == Qt.Checked

        self.line.setVisible(enabled)
        self.cross_section_container.setVisible(enabled)

        # When disabling, save current states and uncheck
        if not enabled:
            self.prev_cursor_toggle_state = self.cursor_toggle_cb.isChecked()
            self.prev_cursor_lines_toggle_state = self.cursor_lines_toggle_cb.isChecked()
            self.cursor_toggle_cb.setChecked(False)
            self.cursor_lines_toggle_cb.setChecked(False)
            self.cursor_toggle_cb.setEnabled(False)
            self.cursor_lines_toggle_cb.setEnabled(False)
        else:
            # Re-enable and restore previous checked states
            self.cursor_toggle_cb.setEnabled(True)
            self.cursor_lines_toggle_cb.setEnabled(True)
            self.cursor_toggle_cb.setChecked(self.prev_cursor_toggle_state)
            self.cursor_lines_toggle_cb.setChecked(self.prev_cursor_lines_toggle_state)
            self.update_cross_section()  # Restore data
    def update_cross_section(self):
        try:
            pixel_size = 1
            state = self.line.getState()
            start = state['points'][0] + state['pos']
            end = state['points'][1] + state['pos']
            n_samples = 300
            distance = np.hypot(end[0] - start[0], end[1] - start[1])
            physical_length = distance * pixel_size
            x = np.linspace(start[0], end[0], n_samples)  # microns
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

            x_physical = np.linspace(0, physical_length, n_samples)
            if not hasattr(self, 'profile_curve'):
                self.profile_curve = self.cross_section_plot.plot(x_physical,profile, pen='y')
            else:
                self.profile_curve.setData(x_physical,profile)

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
        if not self.cursor_lines_toggle_cb.isChecked():
            return  # Skip if toggle is OFF

        if vb.sceneBoundingRect().contains(pos):
            mouse_point = vb.mapSceneToView(pos)
            x, y = mouse_point.x(), mouse_point.y()
            self.vline.setPos(x)
            self.hline.setPos(y)
            self.vline.show()
            self.hline.show()
            self.cursor_label.setText(f"X: {x:.1f}, Y: {y:.3f}")
        else:
            self.vline.hide()
            self.hline.hide()

    def toggle_cursor_lines(self, state):
        visible = state == Qt.Checked
        self.cursor_line1.setVisible(visible)
        self.cursor_line2.setVisible(visible)
        self.cursor_widget.setVisible(visible)


    def update_cursor_labels(self):
        # Get current profile curve data points (assumes one curve plotted)
        curves = self.cross_section_plot.listDataItems()
        if not curves:
            return
        profile_data = curves[0].getData()
        if profile_data is None:
            return
        x_vals, y_vals = profile_data

        def get_reading(line_roi):
            # line ROI is vertical, get its x-position
            x_pos = line_roi.value()
            # Find closest index on x_vals
            idx = np.argmin(np.abs(x_vals - x_pos))
            y_reading = y_vals[idx] if idx < len(y_vals) else np.nan
            return x_pos, y_reading

        x1, y1 = get_reading(self.cursor_line1)
        x2, y2 = get_reading(self.cursor_line2)

        delta_x = x2-x1
        delta_y = y2-y1

        self.cursor_label1.setText(f"Line1: X={x1:.1f}, Y={y1:.3f}")
        self.cursor_label2.setText(f"Line2: X={x2:.1f}, Y={y2:.3f}")
        self.delta_label_x.setText(f"ΔX= {delta_x:.1f}")
        self.delta_label_y.setText(f"ΔY= {delta_y:.3f}")

    def toggle_cursor_lines_visibility(self, state):
        """Toggle visibility of vline/hline based on checkbox state."""
        if state == Qt.Checked:
            self.vline.show() if self.vline.pos() is not None else self.vline.hide()
            self.hline.show() if self.hline.pos() is not None else self.hline.hide()
        else:
            self.vline.hide()
            self.hline.hide()

    def update_cursor_visibility(self, checked):
        if checked:
            self.cursor_label.show()
            self.vline.show()
            self.hline.show()
        else:
            self.cursor_label.hide()
            self.vline.hide()
            self.hline.hide()



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