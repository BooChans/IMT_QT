import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout, QPushButton
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import LineSegmentROI, InfiniteLine
from scipy.ndimage import map_coordinates
import sys

from automatic_sizing import auto_sizing_sampling, auto_sizing_sampling_fresnel
import matplotlib.pyplot as plt

from SourceSection import SourceSection
from ApertureSection import ApertureSection
from SimulationSection import SimulationSection

class DiffractionPropagator(QMainWindow):
    def __init__(self):
        super().__init__()

        # Instantiate all 3 sections
        self.source_section = SourceSection()
        self.aperture_section = ApertureSection()
        self.simulation_section = SimulationSection()

        # Layout with splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.source_section)
        splitter.addWidget(self.aperture_section)
        splitter.addWidget(self.simulation_section)

        # Create a wrapper central widget with a layout
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)

        # Add splitter and button to the layout
        central_layout.addWidget(splitter)

        # Go Button
        self.go_button = QPushButton("Run Simulation")
        self.go_button.clicked.connect(self.run_simulation)
        central_layout.addWidget(self.go_button)

        self.setCentralWidget(central_widget)

        # Optional: initial run
        # self.run_simulation()

    def run_simulation(self):
        # 1. Get the aperture mask
        aperture_params = self.aperture_section.get_inputs()
        aperture = self.aperture_section.aperture


        # 2. Get the source distribution
        source_params = self.source_section.get_inputs()
        source = self.source_section.light_source

        # 3. Get wavelength, distance, pixel size
        wavelength = float(source_params['wavelength'])
        z = float(aperture_params["simulation_distance"])
        source_size = tuple(map(int,self.source_section.size))
        aperture_size = tuple(map(int,self.aperture_section.aperture_size))
        #dx1,_ = auto_sizing_sampling(z, wavelength, source_size ,aperture_size)
        #dx2,_ = auto_sizing_sampling_fresnel(z, wavelength, source_size ,aperture_size)
        dx=1
        #print(dx, dx1, dx2)

        # 4. Update simulation
        self.simulation_section.update_diffraction(source, aperture, wavelength, z, dx)



if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = DiffractionPropagator()
    window.show()
    app.exec()

