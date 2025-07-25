import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout,QGraphicsLineItem, QComboBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import LineSegmentROI, InfiniteLine
from scipy.ndimage import map_coordinates
from resizing_ import format_if_large

class RealTimeCrossSectionViewer(QWidget):
    """
    A PyQt5-based reusable widget for interactively exploring 2D slices from a 3D volume 
    and extracting line profile cross-sections in real time.
    """
    def __init__(self, volume_data, parent=None):
        super().__init__(parent)
        self.volume = volume_data
        self.current_slice = 0
        self.sampling = 1.0
        self.samplings = None
        self.distances = None
        self.wavelengths = None
        self.unit_distance = "µm"
        self.setup_ui()
        self.add_overlay_scale_bar(pixel_length=10)
        self.setup_interaction()
    def setup_ui(self):
        self.setWindowTitle("FFT Cross-Section Viewer")
        self.central_widget = QWidget()

        self.splitter = QSplitter(Qt.Vertical, self)
        self.splitter.setSizes([700, 300])

        self.layout = QVBoxLayout(self)
        
        self.slice_view = pg.ImageView()
        self.slice_view.sigTimeChanged.connect(self.on_time_changed)

        self.slice_view.ui.roiBtn.hide()
        self.slice_view.ui.menuBtn.hide()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setValue(0)

        self.slice_view.setImage(self.volume, xvals=np.arange(self.volume.shape[0]))
        self.slider_visibility()
        self.splitter.addWidget(self.slice_view)
        view = self.slice_view.getView()
        view.setRange(xRange=(0, self.volume.shape[2]), yRange=(0, self.volume.shape[1]), padding=0)

        center_x, center_y = self.volume.shape[2]//2, self.volume.shape[1]//2  # (x_center, y_center)
        offset = 25

        self.line = LineSegmentROI(
            positions=[[center_x - offset, center_y], [center_x + offset, center_y]],
            pen=pg.mkPen('r', width=3),
            movable=True,
            rotatable=True,
            resizable=True
        )
        self.slice_view.getView().addItem(self.line, ignoreBounds=True)

        self.cross_section_container = QWidget()
        cross_layout = QVBoxLayout(self.cross_section_container)
        self.cross_section_plot = pg.PlotWidget()
        cross_layout.addWidget(self.cross_section_plot)


        self.splitter.addWidget(self.cross_section_container)
        self.layout.addWidget(self.splitter)

        self.window_info_widget = QLabel(f"Matrix Size = {self.volume.shape[1]} x {self.volume.shape[2]}, Pixel size = {format_if_large(self.sampling)} {self.unit_distance}")
        self.layout.addWidget(self.window_info_widget)


        self.toggle_line_cb = QCheckBox("Line Profile")
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
        
        self.cursor_toggle_cb.hide()
        self.cursor_toggle_cb.setChecked(False) 
        self.cursor_widget.setVisible(False)

        self.cursor_lines_toggle_cb.hide()
        self.cursor_lines_toggle_cb.setChecked(False) 
        self.cursor_label.setVisible(False)

        self.display_widget = QWidget()
        self.display_widget_layout = QHBoxLayout(self.display_widget)
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Intensity", "Amplitude", "Log-Amplitude", "Phase"])
        self.mode_selector.currentIndexChanged.connect(self.update_display_mode)
        self.mode_selector.currentIndexChanged.connect(self.on_time_changed)
        self.display_widget_layout.addWidget(QLabel("Display Mode:"))
        self.display_widget_layout.addSpacing(20)
        self.display_widget_layout.addWidget(self.mode_selector)
        self.display_widget_layout.addStretch()

        self.layout.addWidget(self.display_widget)





    def setup_interaction(self):
        self.line.sigRegionChanged.connect(self.update_cross_section)
        self.cross_section_plot.scene().sigMouseMoved.connect(self.mouse_moved_on_plot)
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
            self.cursor_toggle_cb.hide()
            self.cursor_lines_toggle_cb.hide()
        else:
            # Re-enable and restore previous checked states
            self.cursor_toggle_cb.setEnabled(True)
            self.cursor_lines_toggle_cb.setEnabled(True)
            self.cursor_toggle_cb.setChecked(self.prev_cursor_toggle_state)
            self.cursor_lines_toggle_cb.setChecked(self.prev_cursor_lines_toggle_state)
            self.cursor_toggle_cb.show()
            self.cursor_lines_toggle_cb.show()
            self.update_cross_section()  # Restore data
    def update_cross_section(self):
        try:
            volume = self.apply_display_mode()
            pixel_size = self.sampling
            state = self.line.getState()
            start = state['points'][0] + state['pos']
            end = state['points'][1] + state['pos']
            n_samples = 300
            distance = np.hypot(end[0] - start[0], end[1] - start[1])
            physical_length = distance * pixel_size
            x = np.linspace(start[1], end[1], n_samples)  # microns
            y = np.linspace(start[0], end[0], n_samples)
            valid_mask = (x >= 0) & (x <= volume.shape[2] - 1) & \
                        (y >= 0) & (y <= volume.shape[1] - 1)

            x_safe = np.copy(x)
            y_safe = np.copy(y)
            x_safe[~valid_mask] = -1
            y_safe[~valid_mask] = -1

            x = np.clip(x, 0, volume.shape[2] - 1)
            y = np.clip(y, 0, volume.shape[1] - 1)

            profile = map_coordinates(
                volume[self.current_slice],
                np.vstack([y, x]),
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

    def update_cross_section_slice(self, slice_data):
            
            volume = slice_data
            pixel_size = self.sampling
            state = self.line.getState()
            start = state['points'][0] + state['pos']
            end = state['points'][1] + state['pos']
            n_samples = 300
            distance = np.hypot(end[0] - start[0], end[1] - start[1])
            physical_length = distance * pixel_size
            x = np.linspace(start[1], end[1], n_samples)  # microns
            y = np.linspace(start[0], end[0], n_samples)
            valid_mask = (x >= 0) & (x <= volume.shape[2] - 1) & \
                         (y >= 0) & (y <= volume.shape[1] - 1)

            x_safe = np.copy(x)
            y_safe = np.copy(y)
            x_safe[~valid_mask] = -1
            y_safe[~valid_mask] = -1

            x = np.clip(x, 0, volume.shape[2] - 1)
            y = np.clip(y, 0, volume.shape[1] - 1)

            profile = map_coordinates(
                slice_data[0],
                np.vstack([y, x]),
                order=1,
                mode='constant',
                cval=0.0
            )

            profile[~valid_mask] = 0

            x_physical = np.linspace(0, physical_length, n_samples)
            if not hasattr(self, 'profile_curve'):
                self.profile_curve = self.cross_section_plot.plot(x_physical,profile, pen='y')
            else:
                self.profile_curve.setData(x_physical, profile)


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
    def update_data(self, new_source, eod = False):
        self.volume = new_source
        volume = self.apply_display_mode()
        self.current_slice = 0
        self.slice_view.setImage(volume, xvals=np.arange(volume.shape[0]))
        self.slider_visibility()
        self.update_line()
        self.window_info_widget.setText(f"Matrix Size = {self.volume.shape[1]} x {self.volume.shape[2]}, Pixel size = {format_if_large(self.sampling)} {self.unit_distance}")
        if not eod:
            lower, upper = np.percentile(volume, [1, 99.98])
            self.slice_view.setLevels(lower, upper)



    def update_data_ap(self, new_source): #useful only for apertures
        volume = self.apply_display_mode_manual(new_source,"Intensity")
        self.current_slice = 0
        self.slice_view.setImage(volume, xvals=np.arange(volume.shape[0]))
        self.slider_visibility()

    def add_overlay_scale_bar(self, pixel_length=100):
        """
        Adds a floating overlay scale bar that stays in the same screen position.
        The bar represents a length in data units (pixels * sampling).
        """
        view = self.slice_view.getView()
        scene = view.scene()

        # Remove existing overlay if needed
        if hasattr(self, '_overlay_bar'):
            scene.removeItem(self._overlay_bar)
            scene.removeItem(self._overlay_label)

        # Create bar in scene coords (temporary, will reposition)
        self._overlay_bar = QGraphicsLineItem()
        self._overlay_bar.setPen(pg.mkPen((255, 165, 0), width=4))
        scene.addItem(self._overlay_bar)

        # Create label
        self._overlay_label = pg.TextItem(
            html=f"<div style='color:orange; font-weight: bold; font-size: 8pt;'>{pixel_length * self.sampling:.2f} µm</div>",
            anchor=(0, 1)
        )
        scene.addItem(self._overlay_label)

        # Store for updates
        self._overlay_length = pixel_length

        # Hook into updates
        view.sigRangeChanged.connect(self.update_overlay_scale_bar_position)
        self.update_overlay_scale_bar_position()

    def update_overlay_scale_bar_position(self):
        """
        Updates the screen position and size of the overlay scale bar.
        Ensures the bar does not exceed a certain fraction of the view width.
        """
        view = self.slice_view.getView()
        vb = view
        scene = view.scene()
        pixel_length = self._overlay_length
        max_fraction = 0.25  # scale bar won't be more than 25% of view width

        # Get viewable data range in x-axis (in data units)
        view_range = vb.viewRange()
        x_range = view_range[0]
        max_data_length = (x_range[1] - x_range[0]) * max_fraction

        # Clamp the length if needed
        clamped_length = min(pixel_length, max_data_length)

        # Transform clamped length to scene units
        p1 = vb.mapViewToScene(pg.QtCore.QPointF(0, 0))
        p2 = vb.mapViewToScene(pg.QtCore.QPointF(clamped_length, 0))
        bar_length_scene = p2.x() - p1.x()

        # Position the bar at bottom-left corner of the view
        view_rect = vb.sceneBoundingRect()
        margin = 20  # pixels
        y = view_rect.bottom() - margin
        x_start = view_rect.left() + margin
        x_end = x_start + bar_length_scene

        self._overlay_bar.setLine(x_start, y, x_end, y)

        # Update label text and position
        physical_length = clamped_length * self.sampling
        self._overlay_label.setHtml(
            f"<div style='color:orange; font-weight: bold; font-size: 8pt;'>{format_if_large(physical_length)} {self.unit_distance}</div>"
        )
        self._overlay_label.setPos((x_start + x_end) / 2, y - 10)

    def update_line(self):

        was_visible = self.line.isVisible() if hasattr(self, "line") else False

        if hasattr(self, "line") and self.line is not None:
            self.slice_view.getView().removeItem(self.line)

        # Get the new center
        center_x, center_y = self.volume.shape[1]//2, self.volume.shape[2]//2  # (x_center, y_center)
        offset = 25

        # Create new line centered on centroid
        self.line = LineSegmentROI(
            positions=[[center_x - offset, center_y], [center_x + offset, center_y]],
            pen=pg.mkPen('r', width=3),
            movable=True,
            rotatable=True,
            resizable=True
        )
        self.slice_view.getView().addItem(self.line, ignoreBounds=True)
        self.line.setVisible(was_visible)
    
        # Reconnect signal
        self.line.sigRegionChanged.connect(self.update_cross_section)

        # Only update cross-section if line is meant to be visible
        if was_visible:
            self.update_cross_section()

    def slider_visibility(self):
        if self.volume.shape[0] == 1:
            self.slice_view.ui.roiPlot.hide()

        else:
            self.slice_view.ui.roiPlot.show()

    def update_display_mode(self):
        volume = self.apply_display_mode()
        self.current_slice = 0
        self.slice_view.setImage(volume, xvals=np.arange(volume.shape[0]))
        self.slider_visibility()
        self.update_line()
        self.window_info_widget.setText(f"Matrix Size = {self.volume.shape[1]} x {self.volume.shape[2]}, Pixel size = {format_if_large(self.sampling)} {self.unit_distance}")

    def apply_display_mode(self):
        mode = self.mode_selector.currentText()
        if mode == "Amplitude":
            return np.abs(self.volume)
        elif mode == "Intensity":
            return np.abs(self.volume) ** 2
        elif mode == "Log-Amplitude":
            return np.log1p(np.abs(self.volume))  # log(1 + amplitude)
        elif mode == "Phase":
            return np.angle(self.volume)
        else:
            return np.abs(self.volume)
        
    def apply_display_mode_manual(self,new_source,mode):
        if mode == "Amplitude":
            return np.abs(new_source)
        elif mode == "Intensity":
            return np.abs(new_source) ** 2
        elif mode == "Log-Amplitude":
            return np.log(np.abs(new_source))  # log(1 + amplitude)
        elif mode == "Phase":
            return np.angle(new_source)
        else:
            return np.abs(new_source)
        
    def apply_display_mode_slice(self, slice):
        mode = self.mode_selector.currentText()
        if mode == "Amplitude":
            return np.abs(slice)
        elif mode == "Intensity":
            return np.abs(slice) ** 2
        elif mode == "Log-Amplitude":
            return np.log1p(np.abs(slice))  # log(1 + amplitude)
        elif mode == "Phase":
            return np.angle(slice)
        else:
            return np.abs(slice)

    def wavelength_to_rgb(self,wavelength):
        """
        Convert a wavelength in nm (380 to 750) to an RGB color.
        Returns an array [R,G,B] with values 0-255.
        """
        if wavelength >= 380 and wavelength <= 750:
            gamma = 0.8
            intensity_max = 1

            if wavelength < 380 or wavelength > 750:
                return np.array([0, 0, 0], dtype=np.uint8)

            if 380 <= wavelength <= 440:
                attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
                R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
                G = 0.0
                B = (1.0 * attenuation) ** gamma
            elif 440 < wavelength <= 490:
                R = 0.0
                G = ((wavelength - 440) / (490 - 440)) ** gamma
                B = 1.0
            elif 490 < wavelength <= 510:
                R = 0.0
                G = 1.0
                B = (-(wavelength - 510) / (510 - 490)) ** gamma
            elif 510 < wavelength <= 580:
                R = ((wavelength - 510) / (580 - 510)) ** gamma
                G = 1.0
                B = 0.0
            elif 580 < wavelength <= 645:
                R = 1.0
                G = (-(wavelength - 645) / (645 - 580)) ** gamma
                B = 0.0
            else:  # 645 < wavelength <= 750
                attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
                R = (1.0 * attenuation) ** gamma
                G = 0.0
                B = 0.0

            R = int(max(0, min(1, R)) * 255)
            G = int(max(0, min(1, G)) * 255)
            B = int(max(0, min(1, B)) * 255)
            color = np.array([R, G, B, 1], dtype=np.uint8)
        else:
            color = np.array([0, 0, 0, 0])
        return color
    
    def update_color(self, wavelength):
        conversion = {"µm":1e3, "mm": 1e6, "m": 1e9}
        wavelength = wavelength * conversion[self.unit_distance]
        color = self.wavelength_to_rgb(wavelength)

        R,G,B,V = color

        if V == 1:
            lut = np.zeros((256, 3), dtype=np.uint8)
            lut[:, 0] = np.linspace(0, R, 256)  
            lut[:, 1] = np.linspace(0, G, 256)  
            lut[:, 2] = np.linspace(0, B, 256)  

            self.slice_view.setColorMap(pg.ColorMap(pos=np.linspace(0,1,256), color=lut))
        else: 
            gray_lut = pg.ColorMap(pos=[0, 1], color=[[0, 0, 0], [255, 255, 255]])
            self.slice_view.setColorMap(gray_lut)

    def on_time_changed(self):
        if len(self.volume) > 1:
            idx = int(self.slice_view.currentIndex)  # current slice index
            slice_data = self.volume[idx][np.newaxis, :]
            slice_data = self.apply_display_mode_slice(slice_data)
            lower, upper = np.percentile(slice_data, [1, 99.98])
            self.sampling = self.samplings[idx]
            self.update_cross_section_slice(slice_data)
            self.update_overlay_scale_bar_position()
            if self.distances is not None:
                self.window_info_widget.setText(f"Matrix Size = {self.volume.shape[1]} x {self.volume.shape[2]}, Pixel size = {format_if_large(self.sampling)} {self.unit_distance}, Simulation distance = {format_if_large(self.distances[idx])}{self.unit_distance}")
            elif self.wavelengths is not None:
                self.window_info_widget.setText(f"Matrix Size = {self.volume.shape[1]} x {self.volume.shape[2]}, Pixel size = {format_if_large(self.sampling)} {self.unit_distance}, Wavelength = {format_if_large(self.wavelengths[idx])}{self.unit_distance}")
                self.update_color(self.wavelengths[idx])
            else:
                self.window_info_widget.setText(f"Matrix Size = {self.volume.shape[1]} x {self.volume.shape[2]}, Pixel size = {format_if_large(self.sampling)} {self.unit_distance}")
            self.slice_view.setLevels(lower, upper)



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