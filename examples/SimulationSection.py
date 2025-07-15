import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout, QRadioButton, QComboBox, QLineEdit,QHBoxLayout, QPushButton, QProgressBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from pyqtgraph import LineSegmentROI, InfiniteLine
from scipy.ndimage import map_coordinates
import sys

from ressource_path import resource_path
from DiffractionSection import RealTimeCrossSectionViewer
from diffraction_propagation import far_field, near_field, angular_spectrum, sweep, sweep_w, fraunhofer
from resizing_ import crop_to_signal, format_if_large
from GenericThread import GenericThread


class SimulationSection(QWidget):
    def __init__(self):
        super().__init__()
        self.unit_distance = "µm"
        self.sampling = "1.0" #user defined sampling for the aperture and the source
        self.volume = np.zeros((1, 512,512))
        self.resolution_multiplier = "1"
        self.start_sweep = "1e2"
        self.end_sweep = "1e4"
        self.step_sweep = "100"

        self.start_sweep_w = "0.380"
        self.end_sweep_w = "0.750"
        self.step_sweep_w = "0.01"
        self.graph_widget = RealTimeCrossSectionViewer(self.volume)

        self.sim_thread = None

        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.addWidget(QLabel("Diffraction pattern"))
        self.widget_layout.addWidget(self.graph_widget)

        self.resolution_widget = QWidget()
        self.resolution_widget_layout = QHBoxLayout(self.resolution_widget)

        resolution_label = QLabel("Over-sample output plane")
        self.combo_res = QComboBox()
        self.combo_res.addItems(["1","2", "4"])      
        self.combo_res.setCurrentText(self.resolution_multiplier)  

        self.resolution_widget_layout.addWidget(resolution_label)
        self.resolution_widget_layout.addStretch()
        self.resolution_widget_layout.addWidget(self.combo_res)

        self.widget_layout.addWidget(self.resolution_widget)
        self.checkbox_widget = QWidget() #alignment
        self.checkbox_widget_layout = QHBoxLayout(self.checkbox_widget)
        self.checkbox = QCheckBox("Manual sampling")

        
        self.checkbox_widget_layout.addWidget(self.checkbox)

        self.sampling_selection_widget = QWidget()
        self.sampling_selection_widget_layout = QHBoxLayout(self.sampling_selection_widget)

        sampling_label = QLabel("Define sampling")

        self.sampling_line_edit=QLineEdit()
        self.sampling_line_edit.setFixedWidth(100)
        self.sampling_line_edit.setText(self.sampling)

        self.combo = QComboBox()
        self.combo.addItems(["µm","mm", "m"])
        self.combo.setCurrentText(self.unit_distance)

        self.sampling_selection_widget_layout.addWidget(sampling_label)
        self.sampling_selection_widget_layout.addStretch()
        self.sampling_selection_widget_layout.addWidget(self.sampling_line_edit)
        self.sampling_selection_widget_layout.addWidget(self.combo)

        self.sampling_line_edit.setEnabled(False)
        self.combo.setEnabled(False)

        self.widget_layout.addWidget(self.checkbox_widget)
        self.widget_layout.addWidget(self.sampling_selection_widget)


        self.algo_label = QLabel("")
        self.widget_layout.addWidget(self.algo_label)

        self.checkbox_sweep = QCheckBox("Z Sweep")
        self.widget_layout.addWidget(self.checkbox_sweep)

        self.sweep_widget = QWidget()
        self.sweep_widget_layout = QHBoxLayout(self.sweep_widget)

        self.sweep_widget_layout.addWidget(QLabel("start : end : step"))
        self.sweep_widget_layout.addStretch()

        self.start_sweep_line_edit = QLineEdit()
        self.start_sweep_line_edit.setText(self.start_sweep)

        self.end_sweep_line_edit = QLineEdit()
        self.end_sweep_line_edit.setText(self.end_sweep)
        
        self.step_sweep_line_edit = QLineEdit()
        self.step_sweep_line_edit.setText(self.step_sweep)

        self.sweep_widget_layout.addWidget(self.start_sweep_line_edit)
        self.sweep_widget_layout.addWidget(self.end_sweep_line_edit)
        self.sweep_widget_layout.addWidget(self.step_sweep_line_edit)

        

        self.widget_layout.addWidget(self.sweep_widget)
        self.sweep_widget.hide()

        self.checkbox_sweep_w = QCheckBox("Wavelength Sweep")
        self.widget_layout.addWidget(self.checkbox_sweep_w)

        self.sweep_widget_w = QWidget()
        self.sweep_widget_w_layout = QHBoxLayout(self.sweep_widget_w)

        self.sweep_widget_w_layout.addWidget(QLabel("start : end : step"))
        self.sweep_widget_w_layout.addStretch()

        self.start_sweep_w_line_edit = QLineEdit()
        self.start_sweep_w_line_edit.setText(self.start_sweep_w)

        self.end_sweep_w_line_edit = QLineEdit()
        self.end_sweep_w_line_edit.setText(self.end_sweep_w)
        
        self.step_sweep_w_line_edit = QLineEdit()
        self.step_sweep_w_line_edit.setText(self.step_sweep_w)

        self.sweep_widget_w_layout.addWidget(self.start_sweep_w_line_edit)
        self.sweep_widget_w_layout.addWidget(self.end_sweep_w_line_edit)
        self.sweep_widget_w_layout.addWidget(self.step_sweep_w_line_edit)

        

        self.widget_layout.addWidget(self.sweep_widget_w)
        self.sweep_widget_w.hide()
        #self.sweep_w_widget.hide()

        # Create progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum = 0
        self.progress.setMaximum = 100
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #CCC;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00CC66;
                width: 1px;
            }
        """)
        self.progress.hide()

        # Create button
        self.go_button = QPushButton("Run Simulation")
        self.go_button.setIcon(QIcon(resource_path("icons/arrows.png")))
        self.go_button.setIconSize(QSize(24, 24))

        self.sweep_button = QPushButton("Z Sweep")
        self.sweep_button.setIcon(QIcon(resource_path("icons/game.png")))  # Change icon if needed
        self.sweep_button.setIconSize(QSize(24, 24))

        self.sweep_button_w = QPushButton("Wavelength Sweep")
        self.sweep_button_w.setIcon(QIcon(resource_path("icons/blue_arrow.png")))  # Change icon if needed
        self.sweep_button_w.setIconSize(QSize(24, 24))

        # Style it
        button_style = """
            QPushButton {{
                font-size: 16px;
                padding: 10px 20px;
                border: 2px solid {color};
                border-radius: 8px;
                color: black;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """

        self.go_button.setStyleSheet(button_style.format(color="green", hover="#eaffea"))
        self.sweep_button.setStyleSheet(button_style.format(color="red", hover="#ffeaea"))
        self.sweep_button_w.setStyleSheet(button_style.format(color="blue", hover="#b9dbfe"))

        self.sweep_button.hide()
        self.sweep_button_w.hide()
        # Fix the button size (optional)
        self.go_button.setFixedWidth(200)  # or whatever width looks good
        self.sweep_button.setFixedWidth(200)  # or whatever width looks good
        self.sweep_button_w.setFixedWidth(200)

        # Right-align the button using a layout
        right_layout = QHBoxLayout()
        right_layout.addWidget(self.go_button)
        right_layout.addWidget(self.sweep_button)  # pushes the button to the left
        right_layout.addWidget(self.sweep_button_w)
        right_layout.addWidget(self.progress)
        right_layout.addStretch()
        # Add this layout to your main layout
        self.widget_layout.addLayout(right_layout)

    def setup_connections(self):
        self.checkbox.stateChanged.connect(self.update_sampling_input)
        self.combo_res.currentTextChanged.connect(self.update_resolution)
        self.checkbox_sweep.stateChanged.connect(self.update_sweep_visibility)
        self.checkbox_sweep_w.stateChanged.connect(self.update_sweep_w_visibility)


        self.start_sweep_line_edit.editingFinished.connect(self.update_sweep_params)
        self.step_sweep_line_edit.editingFinished.connect(self.update_sweep_params)
        self.end_sweep_line_edit.editingFinished.connect(self.update_sweep_params)

        self.start_sweep_w_line_edit.editingFinished.connect(self.update_sweep_w_params)
        self.step_sweep_w_line_edit.editingFinished.connect(self.update_sweep_w_params)
        self.end_sweep_w_line_edit.editingFinished.connect(self.update_sweep_w_params)

    def get_inputs(self):
        """
        Returns a dictionary with the current values of sampling and unit distance.
        If manual sampling is not enabled or sampling is invalid, returns None for sampling.
        """
        if not self.checkbox.isChecked():
            return {
                "sampling": None,
                "unit": None
            }

        sampling_text = self.sampling_line_edit.text()
        unit = self.combo.currentText()

        try:
            sampling_value = float(sampling_text)
        except ValueError:
            sampling_value = None  # fallback if the input is not a valid float

        return {
            "sampling": sampling_value,
            "unit": unit
        }
    
    def update_diffraction(self, source, aperture, wavelength, z, dx, eod = False):

        assert source.shape == aperture.shape, f"Unmatched array shape. Source {source.shape}, Aperture {aperture.shape}."
        U0 = source * aperture
        z_limit = max(U0.shape) * dx**2 / wavelength
        fraunhofer_limit = (max(U0.shape)*dx)**2/wavelength
        print(fraunhofer_limit, "fraunhofer limit")
        if z < fraunhofer_limit:
            try:
                self.volume = far_field(U0, wavelength, z, dx)
                self.graph_widget.sampling = self.pixout(U0, wavelength, z, dx)
                self.algo_label.setText(f"Fresnel algorithm for z > zlimit, z limit = {format_if_large(z_limit)} {self.unit_distance}")
            except:
                self.volume = angular_spectrum(U0, wavelength, z, dx)
                self.graph_widget.sampling = dx
                self.algo_label.setText(f"Near field algorithm for z <= zlimit , z limit = {format_if_large(z_limit)} {self.unit_distance}")
        else:
            self.volume = fraunhofer(U0)
            self.graph_widget.sampling = self.pixout(U0, wavelength, z, dx)
            self.algo_label.setText(f"Fraunhofer algorithm, z limit = {format_if_large(z_limit)} {self.unit_distance}")
        try: 
            self.graph_widget.update_data(self.volume, eod=eod)
            self.graph_widget.update_cross_section()
            self.graph_widget.update_cursor_labels()
        except Exception as e:
            print(f"Error : {e}")

    def start_update_sweep(self, source, aperture, wavelength, dx):
        assert source.shape == aperture.shape, f"Unmatched array shape. Source {source.shape}, Aperture {aperture.shape}."
        U0 = source * aperture
        z_start = float(self.start_sweep)
        z_step = float(self.step_sweep)
        z_end = float(self.end_sweep)

        self.sim_thread = GenericThread(
            self.update_sweep,
            U0,
            wavelength,
            dx,
            z_start,
            z_end,
            z_step
        )

        self.sim_thread.progress_changed.connect(self.progress.setValue)
        self.sim_thread.finished_with_result.connect(self.on_sweep_done)

        self.progress.show()
        self.progress.setValue(0)

        # Start thread
        self.sim_thread.start()

    def update_sweep(self, U0, wavelength, dx, z_start, z_end, z_step, callback = None):
        try:
            volume, samplings, distances = sweep(U0, wavelength, dx, z_start,z_end, z_step, callback)
        except Exception as e:
            print(f"Update sweep error : {e}")
        return volume, samplings, distances, "distance"



    def on_sweep_done(self, result):
        if result is None:
            return 
        if result[3] == "distance":
            self.volume, self.graph_widget.samplings, self.graph_widget.distances, _ = result
            self.graph_widget.wavelengths = None
        else:
            self.volume, self.graph_widget.samplings, self.graph_widget.wavelengths, _ = result
            self.graph_widget.distances = None
        self.graph_widget.update_data(self.volume)
        self.graph_widget.update_cross_section()
        self.graph_widget.update_cursor_labels()
        self.graph_widget.on_time_changed()
        self.progress.hide()

    def start_update_sweep_w(self, source, aperture, z, dx):
        assert source.shape == aperture.shape, f"Unmatched array shape. Source {source.shape}, Aperture {aperture.shape}."
        U0 = source * aperture
        w_start = float(self.start_sweep_w)
        w_step = float(self.step_sweep_w)
        w_end = float(self.end_sweep_w)

        self.sim_thread = GenericThread(
            self.update_sweep_w,
            U0,
            z,
            dx,
            w_start,
            w_end,
            w_step
        )

        self.sim_thread.progress_changed.connect(self.progress.setValue)
        self.sim_thread.finished_with_result.connect(self.on_sweep_done)

        self.progress.show()
        self.progress.setValue(0)

        # Start thread
        self.sim_thread.start()

    def update_sweep_w(self, U0, z, dx, w_start, w_end, w_step, callback = None):
        try:
            volume, samplings, wavelengths = sweep_w(U0, z, dx, w_start, w_end, w_step, callback)
        except Exception as e:
            print(f"Update sweep error : {e}")
        return volume, samplings, wavelengths, "wavelengths"

    
    def pixout(self, source, wavelength, z, dx):
        N = max(source.shape)
        pixout_ = wavelength * abs(z) / (N * dx)
        return pixout_

    def update_sampling_input(self, state):
        if self.checkbox.isChecked():
            self.sampling_line_edit.setEnabled(True)
            self.combo.setEnabled(True)
        else:
            self.sampling_line_edit.setEnabled(False)
            self.combo.setEnabled(False)

    def update_sampling_line(self):
        sampling_fl = round(float(self.sampling),2)
        sampling_fl = str(sampling_fl)
        self.sampling_line_edit.setText(sampling_fl)

    def update_resolution(self, text):
        self.resolution_multiplier = text

    def update_sweep_visibility(self, checked):
        self.sweep_widget.setVisible(checked)
        self.sweep_button.setVisible(checked)

    def update_sweep_w_visibility(self, checked):
        self.sweep_widget_w.setVisible(checked)
        self.sweep_button_w.setVisible(checked)

    def update_sweep_params(self):
        self.start_sweep = self.start_sweep_line_edit.text()
        self.end_sweep = self.end_sweep_line_edit.text()
        self.step_sweep = self.step_sweep_line_edit.text()

        print(self.step_sweep, self.start_sweep, self.end_sweep)

    def update_sweep_w_params(self):
        self.start_sweep_w = self.start_sweep_w_line_edit.text()
        self.end_sweep_w = self.end_sweep_w_line_edit.text()
        self.step_sweep_w = self.step_sweep_w_line_edit.text()

        print(self.step_sweep_w, self.start_sweep_w, self.end_sweep_w)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulationSection()
    window.show()
    app.exec()