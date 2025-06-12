import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout, QRadioButton, QComboBox, QLineEdit,QHBoxLayout,
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import LineSegmentROI, InfiniteLine
from scipy.ndimage import map_coordinates
import sys

from DiffractionSection import RealTimeCrossSectionViewer
from diffraction_propagation import far_field, near_field


class SimulationSection(QWidget):
    def __init__(self):
        super().__init__()
        self.unit_distance = "µm"
        self.sampling = "1.0" #user defined sampling for the aperture and the source
        self.volume = np.zeros((1, 512,512))
        self.resolution_multiplier = "1"
        self.graph_widget = RealTimeCrossSectionViewer(self.volume)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.addWidget(QLabel("Diffraction pattern"))
        self.widget_layout.addWidget(self.graph_widget)

        self.resolution_widget = QWidget()
        self.resolution_widget_layout = QHBoxLayout(self.resolution_widget)

        resolution_label = QLabel("Select output resolution")
        self.combo_res = QComboBox()
        self.combo_res.addItems(["1","2", "4", "8"])      
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
    
    def setup_connections(self):
        self.checkbox.stateChanged.connect(self.update_sampling_input)
        self.combo_res.currentTextChanged.connect(self.update_resolution)

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
    
    def update_diffraction(self, source, aperture, wavelength, z, dx):

        assert source.shape == aperture.shape, f"Unmatched array shape. Source {source.shape}, Aperture {aperture.shape}."
        U0 = source * aperture
        try:
            self.volume = far_field(U0, wavelength, z, dx)
            self.graph_widget.sampling = self.pixout(U0, wavelength, z, dx)
        except:
            self.volume = near_field(U0, wavelength, z, dx)
        self.graph_widget.update_data(self.volume)
        self.graph_widget.update_cross_section()
        self.graph_widget.update_cursor_labels()
    
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
