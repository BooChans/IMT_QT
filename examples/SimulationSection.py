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
from automatic_sizing import auto_sizing_sampling


class SimulationSection(QWidget):
    def __init__(self):
        super().__init__()

        self.volume = np.zeros((1, 512,512))
        self.graph_widget = RealTimeCrossSectionViewer(self.volume)
        self.setup_ui()
    
    def setup_ui(self):
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.addWidget(self.graph_widget)

    
    def update_diffraction(self, source, aperture, wavelength, z, dx):

        assert source.shape == aperture.shape, f"Unmatched array shape. Source {source.shape}, Aperture {aperture.shape}."
        U0 = source * aperture
        try:
            self.volume = far_field(U0, wavelength, z, dx)
            print("far_field")
        except:
            self.volume = near_field(U0, wavelength, z, dx)
            print("near_field")
        self.graph_widget.update_data(self.volume)
        self.graph_widget.update_cross_section()
        self.graph_widget.update_cursor_labels()